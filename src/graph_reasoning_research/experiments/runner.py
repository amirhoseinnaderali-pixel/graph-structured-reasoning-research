from __future__ import annotations

import hashlib
import time
from pathlib import Path

from graph_reasoning_research.aggregation.baselines import (
    consensus,
    first_candidate,
    graph_ranking,
    objective_verification,
    random_candidate,
    similarity_ranking,
)
from graph_reasoning_research.budgeting.budget import BudgetLedger
from graph_reasoning_research.generation.base import MockCandidateGenerator, assert_same_candidate_set
from graph_reasoning_research.graph.builders import knn_graph, threshold_graph
from graph_reasoning_research.logging.schema import append_jsonl
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.types import RunRecord, Selection
from graph_reasoning_research.verification.objective import MockObjectiveVerifier


def _run_id(seed: int, task_id: str) -> str:
    return hashlib.sha256(f"EXP-001|{seed}|{task_id}".encode("utf-8")).hexdigest()[:16]


def run_mock(config: dict, output_path: str | Path) -> list[dict]:
    generator = MockCandidateGenerator()
    representation_provider = HashEmbeddingProvider()
    verifier = MockObjectiveVerifier()
    rows: list[dict] = []
    tasks = [("mock-001", "return 1"), ("mock-002", "return 0")]

    for seed in config["seeds"]:
        for task_id, problem in tasks:
            ledger = BudgetLedger(
                max_generation_calls=config["candidate_count"],
                max_generation_input_tokens=8192,
                max_generation_output_tokens=8192,
                max_representation_calls=8,
                max_verification_executions=64,
            )
            ledger.reserve_generation(calls=config["candidate_count"])
            candidate_set = generator.generate(task_id, problem, config["candidate_count"], seed)
            representation_start = time.perf_counter()
            ledger.reserve_representation()
            representation = representation_provider.encode(candidate_set)
            representation_latency_ms = (time.perf_counter() - representation_start) * 1000

            similarity_start = time.perf_counter()
            similarity = cosine_similarity_matrix(representation.embeddings)
            similarity_latency_ms = (time.perf_counter() - similarity_start) * 1000
            similarity_config = {"function": "cosine", "normalized": True}

            graph_start = time.perf_counter()
            threshold = threshold_graph(candidate_set.ids(), similarity, 0.25, True)
            knn = knn_graph(candidate_set.ids(), similarity, 2, False)
            graph_construction_latency_ms = (time.perf_counter() - graph_start) * 1000

            graph_score_start = time.perf_counter()
            graph_threshold_selection = graph_ranking(candidate_set, threshold, "weighted_degree")
            graph_knn_selection = graph_ranking(candidate_set, knn, "degree_centrality")
            graph_scoring_latency_ms = (time.perf_counter() - graph_score_start) * 1000

            objective_by_id = {
                candidate.candidate_id: float((i + seed) % 2 == 1)
                for i, candidate in enumerate(candidate_set.candidates)
            }
            selections: list[Selection] = [
                first_candidate(candidate_set),
                random_candidate(candidate_set, seed),
                consensus(candidate_set),
                similarity_ranking(candidate_set, similarity),
                graph_threshold_selection,
                graph_knn_selection,
                objective_verification(candidate_set, objective_by_id),
            ]
            shortlist = sorted(
                graph_threshold_selection.scores,
                key=lambda c: (-graph_threshold_selection.scores[c], c),
            )[:2]
            shortlist_scores = {candidate_id: objective_by_id[candidate_id] for candidate_id in shortlist}
            shortlist_set = candidate_set.__class__(
                candidate_set.task_id,
                tuple(c for c in candidate_set.candidates if c.candidate_id in shortlist),
                candidate_set.candidate_set_hash,
            )
            selections.append(
                Selection(
                    "graph+objective_verification",
                    objective_verification(shortlist_set, shortlist_scores).selected_candidate_id,
                    shortlist_scores,
                    {"graph_priority": True, "shortlist": shortlist},
                )
            )

            assert_same_candidate_set(candidate_set)
            aggregation_latency_ms = (
                representation_latency_ms
                + similarity_latency_ms
                + graph_construction_latency_ms
                + graph_scoring_latency_ms
            )
            graph_stats = {
                "nodes": len(threshold.nodes),
                "edges": len(threshold.edges),
                "density": (2 * len(threshold.edges))
                / (len(threshold.nodes) * (len(threshold.nodes) - 1))
                if len(threshold.nodes) > 1
                else 0.0,
            }

            for selection in selections:
                ledger.reserve_verification()
                visible_start = time.perf_counter()
                visible = verifier.evaluate_visible(
                    next(
                        c
                        for c in candidate_set.candidates
                        if c.candidate_id == selection.selected_candidate_id
                    )
                )
                visible_latency_ms = (time.perf_counter() - visible_start) * 1000
                row = RunRecord(
                    experiment_id="EXP-001",
                    run_id=_run_id(seed, task_id),
                    task_id=task_id,
                    seed=seed,
                    aggregation_method=selection.method,
                    representation_method=representation.method,
                    representation_config_hash=representation.config_hash,
                    graph_method=selection.method.split(":", 1)[1]
                    if selection.method.startswith("graph:")
                    else None,
                    graph_config_hash=(
                        threshold.config_hash
                        if selection.method == graph_threshold_selection.method
                        else knn.config_hash
                        if selection.method == graph_knn_selection.method
                        else None
                    ),
                    candidate_id=selection.selected_candidate_id,
                    selected_candidate_id=selection.selected_candidate_id,
                    objective_result=visible.objective_result,
                    generation_model_id=candidate_set.candidates[0].generator_model_id,
                    generation_config_hash=candidate_set.candidates[0].generation_config_hash,
                    generation_calls=ledger.generation_calls,
                    generation_input_tokens=ledger.generation_input_tokens,
                    generation_output_tokens=ledger.generation_output_tokens,
                    representation_calls=ledger.representation_calls,
                    representation_tokens=ledger.representation_tokens,
                    embedding_latency_ms=representation_latency_ms,
                    similarity_latency_ms=similarity_latency_ms,
                    representation_latency_ms=representation_latency_ms,
                    graph_construction_latency_ms=graph_construction_latency_ms,
                    graph_scoring_latency_ms=graph_scoring_latency_ms,
                    aggregation_latency_ms=aggregation_latency_ms,
                    visible_verification_latency_ms=visible_latency_ms,
                    hidden_verification_latency_ms=0.0,
                    candidate_set_hash=candidate_set.candidate_set_hash,
                    representation_hash=representation.representation_hash,
                    similarity_config=similarity_config,
                    graph_stats=graph_stats,
                    metadata={
                        "validation_only": True,
                        "candidate_manifest": candidate_set.manifest(),
                        "scores": selection.scores,
                        "selection_metadata": selection.metadata,
                    },
                )
                append_jsonl(output_path, row)
                rows.append(row.__dict__)
    return rows
