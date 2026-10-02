from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
import uuid
from pathlib import Path

from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks, manifest_hash
from graph_reasoning_research.aggregation.baselines import (
    consensus,
    first_candidate,
    graph_ranking,
    random_candidate,
    similarity_ranking,
)
from graph_reasoning_research.budgeting.budget import BudgetLedger
from graph_reasoning_research.experiments.config import config_hash, load_yaml, validate_bundle
from graph_reasoning_research.generation.base import MockCandidateGenerator, assert_same_candidate_set
from graph_reasoning_research.generation.openai import OpenAICandidateGenerator
from graph_reasoning_research.graph.builders import knn_graph, threshold_graph
from graph_reasoning_research.logging.schema import write_jsonl_exclusive
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.representations.feature_hash_tfidf import FeatureHashTfidfProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.types import Candidate, CandidateSet, RunRecord, Selection
from graph_reasoning_research.verification.docker import DockerPythonVerifier


def _run_id() -> str:
    return uuid.uuid4().hex


def _git_sha(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except Exception:
        return None


def _copy_candidate(candidate: Candidate, **metadata: object) -> Candidate:
    return Candidate(
        candidate_id=candidate.candidate_id,
        task_id=candidate.task_id,
        text=candidate.text,
        answer=candidate.answer,
        generator_model_id=candidate.generator_model_id,
        seed=candidate.seed,
        generation_config_hash=candidate.generation_config_hash,
        output_hash=candidate.output_hash,
        metadata={**candidate.metadata, **metadata},
    )


def _selection_record(
    *,
    experiment_id: str,
    run_id: str,
    task: dict,
    seed: int,
    selection: Selection,
    generation: dict,
    representation,
    candidate_set: CandidateSet,
    graph_data,
    graph_time_ms: float,
    graph_score_time_ms: float,
    manifest_sha: str,
    config_hashes: dict[str, str],
    budget: BudgetLedger,
    objective_result: str,
    hidden_eval: dict,
    visible_eval: dict,
    visible_latency_ms: float,
    hidden_latency_ms: float,
    environment: dict,
) -> RunRecord:
    graph_stats = {}
    graph_method = None
    graph_config_hash_value = None
    if graph_data is not None:
        graph_method = graph_data.builder
        graph_config_hash_value = graph_data.config_hash
        n = len(graph_data.nodes)
        graph_stats = {
            "nodes": n,
            "edges": len(graph_data.edges),
            "density": (2 * len(graph_data.edges) / (n * (n - 1))) if n > 1 else 0.0,
        }
    return RunRecord(
        experiment_id=experiment_id,
        run_id=run_id,
        task_id=task["task_id"],
        seed=seed,
        aggregation_method=selection.method,
        representation_method=representation.method,
        representation_config_hash=representation.config_hash,
        graph_method=graph_method,
        graph_config_hash=graph_config_hash_value,
        candidate_id=selection.selected_candidate_id,
        selected_candidate_id=selection.selected_candidate_id,
        objective_result=objective_result,
        generation_model_id=candidate_set.candidates[0].generator_model_id,
        generation_config_hash=candidate_set.candidates[0].generation_config_hash,
        generation_calls=int(generation.get("calls", 0)),
        generation_input_tokens=int(generation.get("prompt_tokens", 0)),
        generation_output_tokens=int(generation.get("completion_tokens", 0)),
        representation_calls=budget.representation_calls,
        representation_tokens=budget.representation_tokens,
        embedding_latency_ms=float(environment["representation_latency_ms"]),
        similarity_latency_ms=float(environment["similarity_latency_ms"]),
        representation_latency_ms=float(environment["representation_latency_ms"]),
        graph_construction_latency_ms=float(graph_time_ms),
        graph_scoring_latency_ms=float(graph_score_time_ms),
        aggregation_latency_ms=float(
            environment["representation_latency_ms"]
            + environment["similarity_latency_ms"]
            + graph_time_ms
            + graph_score_time_ms
        ),
        visible_verification_latency_ms=visible_latency_ms,
        hidden_verification_latency_ms=hidden_latency_ms,
        candidate_set_hash=candidate_set.candidate_set_hash,
        representation_hash=representation.representation_hash,
        similarity_config={"function": "cosine", "normalized_embeddings": True},
        graph_stats=graph_stats,
        benchmark_hash=manifest_sha,
        status=("SUCCESS" if objective_result == "PASS" else "CANDIDATE_FAILURE" if objective_result in {"FAIL", "TIMEOUT"} else "INFRASTRUCTURE_ERROR"),
        error=None if objective_result in {"PASS", "FAIL", "TIMEOUT"} else hidden_eval.get("error"),
        failure_class=hidden_eval.get("failure_class"),
        generation=generation,
        representation={
            "method": representation.method,
            "model_id": representation.model_id,
            "model_revision": representation.model_revision,
            "config_hash": representation.config_hash,
            "representation_hash": representation.representation_hash,
        },
        aggregation={
            "method": selection.method,
            "scores": selection.scores,
            "metadata": selection.metadata,
            "config_hashes": config_hashes,
        },
        visible_evaluation=visible_eval,
        hidden_evaluation=hidden_eval,
        budget={
            "candidate_count": budget.candidate_count,
            "generation_calls": budget.generation_calls,
            "generation_input_tokens": budget.generation_input_tokens,
            "generation_output_tokens": budget.generation_output_tokens,
            "representation_calls": budget.representation_calls,
            "visible_verification_executions": budget.visible_verification_executions,
            "hidden_verification_executions": budget.hidden_verification_executions,
            "elapsed_ms": budget.elapsed_ms,
        },
        environment=environment,
    )


def _prepare_generator(root: Path, config: dict, mode: str):
    model_cfg = load_yaml(root / config["candidate_generator_config"])
    candidate_cfg = model_cfg["candidate_generator"]
    if mode == "mock":
        return MockCandidateGenerator()
    if candidate_cfg["provider"] != "openai":
        raise RuntimeError("real execution rejects non-OpenAI/mock candidate adapters")
    return OpenAICandidateGenerator(candidate_cfg)


def _prepare_representation(root: Path, config: dict, mode: str):
    rep_cfg = load_yaml(root / config["representation_config"])
    if mode == "mock":
        return HashEmbeddingProvider(dimension=32)
    if rep_cfg["method"] != "feature_hash_tfidf":
        raise RuntimeError("real execution representation does not match frozen method")
    return FeatureHashTfidfProvider(dimension=int(rep_cfg["dimension"]))


def run_mock(config: dict, output_path: str | Path) -> list[dict]:
    generator = MockCandidateGenerator()
    representation_provider = HashEmbeddingProvider()
    rows: list[dict] = []
    tasks = [("mock-001", "return 1"), ("mock-002", "return 0")]
    for seed in config["seeds"]:
        for task_id, problem in tasks:
            candidate_set = generator.generate(task_id, problem, config["candidate_count"], seed)
            generation = {"provider":"mock","model_id":generator.model_id,"calls":1,"prompt_tokens":0,"completion_tokens":0,"total_tokens":0,"latency_ms":0.0,"validation_only":True}
            representation = representation_provider.encode(candidate_set)
            similarity = cosine_similarity_matrix(representation.embeddings)
            graph = threshold_graph(candidate_set.ids(), similarity, 0.25, True)
            selection = graph_ranking(candidate_set, graph, "weighted_degree")
            rows.append({
                "experiment_id": "EXP-001",
                "run_id": f"MOCK-{seed}-{task_id}",
                "task_id": task_id,
                "seed": seed,
                "aggregation_method": selection.method,
                "candidate_set_hash": candidate_set.candidate_set_hash,
                "representation_hash": representation.representation_hash,
                "selected_candidate_id": selection.selected_candidate_id,
                "status": "validation_only",
                "generation": generation,
                "metadata": {"validation_only": True},
            })
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return rows


def run_real(
    root: str | Path,
    config: dict,
    *,
    smoke: bool = False,
) -> Path:
    root = Path(root)
    failures = validate_bundle(root, config)
    if failures:
        raise RuntimeError("real preflight failed: " + "; ".join(failures))

    manifest_path = root / config["benchmark_manifest"]
    manifest = load_manifest(manifest_path, require_frozen=True)
    load_materialized_tasks(root / "benchmarks/programming/exp001_v1/tasks.jsonl", manifest)
    manifest_sha = manifest_hash(manifest)

    model_cfg = load_yaml(root / config["candidate_generator_config"])
    rep_cfg = load_yaml(root / config["representation_config"])
    graph_cfg = load_yaml(root / config["graph_config"])
    budget_cfg = load_yaml(root / config["budget_config"])
    runtime_cfg = load_yaml(root / config["runtime_config"])
    config_hashes = {
        "experiment": config_hash(config),
        "model": config_hash(model_cfg),
        "representation": config_hash(rep_cfg),
        "graph": config_hash(graph_cfg),
        "budget": config_hash(budget_cfg),
        "runtime": config_hash(runtime_cfg),
    }

    generator = _prepare_generator(root, config, "real")
    representation_provider = _prepare_representation(root, config, "real")
    verifier = DockerPythonVerifier(
        image=runtime_cfg["docker_image"],
        timeout_seconds=int(runtime_cfg["timeout_seconds"]),
        memory=str(runtime_cfg["memory"]),
        cpus=str(runtime_cfg["cpus"]),
        pids_limit=str(runtime_cfg["pids_limit"]),
        platform=str(runtime_cfg["platform"]),
    )

    run_id = _run_id()
    all_records: list[RunRecord] = []
    seeds = config["seeds"][:1] if smoke else config["seeds"]
    tasks = manifest["tasks"][:1] if smoke else manifest["tasks"]
    total_started = time.perf_counter()

    for seed in seeds:
        for task in tasks:
            ledger = BudgetLedger(
                max_generation_calls=int(budget_cfg["candidate_generation"]["max_calls"]),
                max_generation_input_tokens=int(budget_cfg["candidate_generation"]["max_input_tokens"]),
                max_generation_output_tokens=int(budget_cfg["candidate_generation"]["max_output_tokens"]),
                max_representation_calls=int(budget_cfg["representation"]["max_embedding_calls"]),
                max_visible_verifications=int(budget_cfg["verification"]["max_visible_executions"]),
                max_hidden_verifications=int(budget_cfg["verification"]["max_hidden_executions"]),
                max_aggregation_ms=float(budget_cfg["aggregation"]["max_wall_time_ms"]),
                max_total_wall_ms=float(budget_cfg["total"]["max_wall_time_ms"]),
            )

            ledger.reserve_generation(
                input_tokens=int(budget_cfg["candidate_generation"]["max_input_tokens"]),
                output_tokens=int(budget_cfg["candidate_generation"]["max_output_tokens"]),
                calls=1,
            )
            candidate_set, generation = generator.generate(
                task["task_id"],
                task["problem"],
                int(config["candidate_count"]),
                int(seed),
                entry_point=task["entry_point"],
            )
            ledger.record_candidates(len(candidate_set.candidates))
            if len(candidate_set.candidates) != int(config["candidate_count"]):
                raise RuntimeError("budget_ineligibility: candidate count mismatch")

            representation_started = time.perf_counter()
            ledger.reserve_representation(calls=1)
            representation = representation_provider.encode(candidate_set)
            representation_latency_ms = (time.perf_counter() - representation_started) * 1000.0

            similarity_started = time.perf_counter()
            similarity = cosine_similarity_matrix(representation.embeddings)
            similarity_latency_ms = (time.perf_counter() - similarity_started) * 1000.0

            assert_same_candidate_set(candidate_set)

            selections: list[tuple[Selection, object | None, float, float, dict]] = []
            selections.append((first_candidate(candidate_set), None, 0.0, 0.0, {"condition": "C0"}))
            selections.append((random_candidate(candidate_set, seed), None, 0.0, 0.0, {"condition": "C1"}))
            selections.append((consensus(candidate_set), None, 0.0, 0.0, {"condition": "C2"}))
            selections.append((similarity_ranking(candidate_set, similarity), None, 0.0, 0.0, {"condition": "C3"}))

            graph_started = time.perf_counter()
            primary_graph = threshold_graph(
                candidate_set.ids(),
                similarity,
                float(graph_cfg["primary"]["threshold"]),
                bool(graph_cfg["primary"]["weighted"]),
            )
            graph_build_ms = (time.perf_counter() - graph_started) * 1000.0
            graph_score_started = time.perf_counter()
            primary_selection = graph_ranking(
                candidate_set, primary_graph, graph_cfg["primary"]["scoring"]
            )
            graph_score_ms = (time.perf_counter() - graph_score_started) * 1000.0
            ledger.record_graph(graph_build_ms, graph_score_ms)
            selections.append((primary_selection, primary_graph, graph_build_ms, graph_score_ms, {"condition": "C4"}))

            # C5: graph-derived shortlist, independent visible verification only.
            ranked_shortlist = [
                cid for cid, _ in sorted(
                    primary_selection.scores.items(),
                    key=lambda item: (-float(item[1]), item[0]),
                )
            ][:2]
            visible_scores: dict[str, float] = {}
            visible_results: list[dict] = []
            visible_started = time.perf_counter()
            selected_c5 = ranked_shortlist[0]
            visible_candidate_set = CandidateSet(
                candidate_set.task_id,
                tuple(
                    _copy_candidate(
                        c,
                        visible_tests=task["visible_tests"],
                        entry_point=task["entry_point"],
                    )
                    for c in candidate_set.candidates
                ),
                candidate_set.candidate_set_hash,
            )
            for cid in ranked_shortlist:
                ledger.reserve_visible_verification()
                c = next(x for x in visible_candidate_set.candidates if x.candidate_id == cid)
                evaluation = verifier.evaluate_visible(c)
                visible_results.append({
                    "candidate_id": cid,
                    "result": evaluation.objective_result,
                    "failure_class": evaluation.failure_class,
                })
                visible_scores[cid] = 1.0 if evaluation.objective_result == "PASS" else 0.0
                if evaluation.objective_result == "INFRASTRUCTURE_ERROR":
                    raise RuntimeError(f"verification infrastructure failure: {evaluation.failure_class}")
                if evaluation.objective_result == "PASS":
                    selected_c5 = cid
                    break
            visible_latency_ms = (time.perf_counter() - visible_started) * 1000.0
            c5_selection = Selection(
                "graph+objective_verification",
                selected_c5,
                {cid: visible_scores.get(cid, 0.0) for cid in ranked_shortlist},
                {"condition": "C5", "graph_priority": True, "shortlist": ranked_shortlist, "visible_results": visible_results},
            )
            selections.append((c5_selection, primary_graph, 0.0, 0.0, {"condition": "C5"}))

            # C6: 2 graph builders x 2 edge modes x 4 scoring methods.
            c6_specs = [
                ("threshold", True, scoring)
                for scoring in graph_cfg["scoring"]["methods"]
            ] + [
                ("threshold", False, scoring)
                for scoring in graph_cfg["scoring"]["methods"]
            ] + [
                ("knn", True, scoring)
                for scoring in graph_cfg["scoring"]["methods"]
            ] + [
                ("knn", False, scoring)
                for scoring in graph_cfg["scoring"]["methods"]
            ]
            for builder_name, weighted, scoring in c6_specs:
                started = time.perf_counter()
                if builder_name == "threshold":
                    graph = threshold_graph(
                        candidate_set.ids(),
                        similarity,
                        float(graph_cfg["threshold"]["threshold"]),
                        weighted,
                    )
                else:
                    graph = knn_graph(
                        candidate_set.ids(),
                        similarity,
                        int(graph_cfg["knn"]["k"]),
                        weighted,
                    )
                build_ms = (time.perf_counter() - started) * 1000.0
                score_started = time.perf_counter()
                selection = graph_ranking(candidate_set, graph, scoring)
                score_ms = (time.perf_counter() - score_started) * 1000.0
                ledger.record_graph(build_ms, score_ms)
                selections.append((selection, graph, build_ms, score_ms, {
                    "condition": "C6",
                    "builder": builder_name,
                    "weighted": weighted,
                    "scoring": scoring,
                }))

            if len(selections) != 22:
                raise RuntimeError(f"protocol error: expected 22 selections, got {len(selections)}")

            for selection, graph_data, build_ms, score_ms, selection_meta in selections:
                assert_same_candidate_set(candidate_set)

                hidden_candidate = next(
                    c for c in candidate_set.candidates
                    if c.candidate_id == selection.selected_candidate_id
                )
                hidden_candidate = _copy_candidate(
                    hidden_candidate,
                    hidden_tests=task["hidden_tests"],
                    entry_point=task["entry_point"],
                )
                ledger.reserve_hidden_verification()
                hidden_started = time.perf_counter()
                hidden_eval_result = verifier.evaluate_hidden(hidden_candidate)
                hidden_latency_ms = (time.perf_counter() - hidden_started) * 1000.0
                if hidden_eval_result.objective_result == "INFRASTRUCTURE_ERROR":
                    raise RuntimeError(
                        f"verification infrastructure failure: {hidden_eval_result.failure_class}"
                    )

                env = {
                    "git_sha": _git_sha(root),
                    "python": sys.version,
                    "platform": platform.platform(),
                    "docker_image": runtime_cfg["docker_image"],
                    "model_id": model_cfg["candidate_generator"]["model_id"],
                    "model_revision": model_cfg["candidate_generator"]["model_revision"],
                    "config_hashes": config_hashes,
                    "representation_latency_ms": representation_latency_ms,
                    "similarity_latency_ms": similarity_latency_ms,
                }
                rec = _selection_record(
                    experiment_id="EXP-001",
                    run_id=run_id,
                    task=task,
                    seed=seed,
                    selection=Selection(
                        selection.method,
                        selection.selected_candidate_id,
                        selection.scores,
                        {**selection.metadata, **selection_meta},
                    ),
                    generation=generation,
                    representation=representation,
                    candidate_set=candidate_set,
                    graph_data=graph_data,
                    graph_time_ms=build_ms,
                    graph_score_time_ms=score_ms,
                    manifest_sha=manifest_sha,
                    config_hashes=config_hashes,
                    budget=ledger,
                    objective_result=hidden_eval_result.objective_result,
                    hidden_eval={
                        "objective_result": hidden_eval_result.objective_result,
                        "failure_class": hidden_eval_result.failure_class,
                        "test_visibility": "hidden_only",
                    },
                    visible_eval={
                        "used": selection.method == "graph+objective_verification",
                        "test_visibility": "visible_only",
                        "results": selection.metadata.get("visible_results", []),
                    },
                    visible_latency_ms=visible_latency_ms if selection.method == "graph+objective_verification" else 0.0,
                    hidden_latency_ms=hidden_latency_ms,
                    environment=env,
                )
                all_records.append(rec)

    output_dir = root / ("results/smoke_test" if smoke else "results/raw/EXP-001")
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = "EXECUTION_SMOKE_TEST" if smoke else "EXP-001"
    output_path = output_dir / f"{prefix}-{run_id}.jsonl"
    write_jsonl_exclusive(output_path, all_records)

    if smoke:
        marker = {
            "label": "EXECUTION_SMOKE_TEST",
            "run_id": run_id,
            "records": len(all_records),
            "wall_clock_ms": (time.perf_counter() - total_started) * 1000.0,
            "counts_as_exp001_evidence": False,
        }
        marker_path = output_dir / f"{prefix}-{run_id}.json"
        with marker_path.open("x", encoding="utf-8") as handle:
            json.dump(marker, handle, indent=2, sort_keys=True)
    return output_path
