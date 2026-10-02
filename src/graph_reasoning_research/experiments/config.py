from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require(config: dict, path: str, failures: list[str]) -> Any:
    current: Any = config
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            failures.append(f"missing config field: {path}")
            return None
        current = current[key]
    return current


def validate_config(config: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if config.get("experiment_id") != "EXP-001":
        failures.append("experiment_id must be EXP-001")
    if config.get("status") != "READY_FOR_REAL_EXECUTION":
        failures.append("EXP-001 config must be READY_FOR_REAL_EXECUTION")
    if config.get("mode_policy", {}).get("real_execution_enabled") is not True:
        failures.append("real execution must be enabled in frozen experiment policy")
    if config.get("mode_policy", {}).get("mock_allowed") is not True:
        failures.append("mock mode must remain available for validation")
    seeds = config.get("seeds")
    if not seeds or any(not isinstance(seed, int) for seed in seeds):
        failures.append("explicit integer seeds are required")
    if int(config.get("candidate_count", 0)) < 2:
        failures.append("candidate_count must be >= 2")
    controls = config.get("scientific_controls", {})
    for control in (
        "candidate_set_hashing",
        "hidden_test_isolation",
        "representation_hashing",
        "graph_config_hashing",
        "single_candidate_generation_call_per_task_seed",
        "hidden_evaluation_after_selection_only",
    ):
        if controls.get(control) is not True:
            failures.append(f"scientific control disabled: {control}")
    return failures


def validate_bundle(root: str | Path, config: dict[str, Any]) -> list[str]:
    root = Path(root)
    failures = validate_config(config)
    try:
        from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks
        manifest_path = root / config["benchmark_manifest"]
        manifest = load_manifest(manifest_path, require_frozen=True)
        materialized = root / "benchmarks/programming/exp001_v1/tasks.jsonl"
        load_materialized_tasks(materialized, manifest)
    except Exception as exc:
        failures.append(f"benchmark validation: {exc}")

    frozen_blobs = config.get("frozen_input_blob_shas", {})
    frozen_paths = {
        "candidate_generator_config": config["candidate_generator_config"],
        "representation_config": config["representation_config"],
        "graph_config": config["graph_config"],
        "budget_config": config["budget_config"],
        "runtime_config": config["runtime_config"],
        "pricing_config": config["pricing_config"],
        "benchmark_manifest": config["benchmark_manifest"],
        "benchmark_materialization": "benchmarks/programming/exp001_v1/tasks.jsonl",
    }
    for key, relative_path in frozen_paths.items():
        expected_blob = frozen_blobs.get(key)
        if not expected_blob:
            failures.append(f"missing frozen blob SHA: {key}")
            continue
        try:
            observed_blob = subprocess.check_output(
                ["git", "hash-object", str(root / relative_path)],
                text=True,
            ).strip()
            if observed_blob != expected_blob:
                failures.append(f"frozen blob SHA mismatch: {key}")
        except Exception as exc:
            failures.append(f"unable to hash frozen input {key}: {exc}")

    models = load_yaml(root / config["candidate_generator_config"])
    representation = load_yaml(root / config["representation_config"])
    graph = load_yaml(root / config["graph_config"])
    budget = load_yaml(root / config["budget_config"])
    runtime = load_yaml(root / config["runtime_config"])

    if models.get("status") != "FROZEN":
        failures.append("candidate model config is not FROZEN")
    candidate = models.get("candidate_generator", {})
    for key in ("provider", "model_id", "model_revision", "credential_env", "temperature", "top_p", "max_tokens", "candidate_count", "seed_policy"):
        if key not in candidate or candidate[key] in (None, "", "UNSET"):
            failures.append(f"candidate model config missing {key}")
    if candidate.get("provider") != "openai":
        failures.append("real execution requires the frozen OpenAI adapter")
    if candidate.get("model_id") != "gpt-4.1-mini-2025-04-14":
        failures.append("candidate model ID does not match frozen EXP-001 model")

    if representation.get("status") != "FROZEN":
        failures.append("representation config is not FROZEN")
    for key in ("method", "provider", "model_id", "model_revision", "dimension", "normalize_embeddings", "similarity_function"):
        if representation.get(key) in (None, "", "UNSET"):
            failures.append(f"representation config missing {key}")
    if representation.get("provider") != "local_deterministic":
        failures.append("representation provider must be deterministic local")

    if graph.get("status") != "FROZEN":
        failures.append("graph config is not FROZEN")
    for section in ("threshold", "knn", "weighted", "unweighted", "scoring"):
        if section not in graph:
            failures.append(f"graph config missing section {section}")

    if budget.get("status") != "FROZEN":
        failures.append("budget config is not FROZEN")
    for path in (
        "candidate_generation.max_candidates",
        "candidate_generation.max_calls",
        "candidate_generation.max_input_tokens",
        "candidate_generation.max_output_tokens",
        "representation.max_embedding_calls",
        "verification.max_visible_executions",
        "verification.max_hidden_executions",
        "total.max_wall_time_ms",
    ):
        value = _require(budget, path, failures)
        if isinstance(value, (int, float)) and value <= 0:
            failures.append(f"budget field must be positive: {path}")
    if int(config["candidate_count"]) != int(budget["candidate_generation"]["max_candidates"]):
        failures.append("candidate_count must equal frozen generation max_candidates")

    if runtime.get("status") != "FROZEN":
        failures.append("runtime config is not FROZEN")
    image = str(runtime.get("docker_image", ""))
    if "@sha256:" not in image:
        failures.append("runtime Docker image must be digest-pinned")
    if runtime.get("network") != "none" or runtime.get("read_only_root") is not True:
        failures.append("runtime sandbox policy is not frozen to network=none/read-only")
    if runtime.get("no_new_privileges") is not True or runtime.get("drop_all_capabilities") is not True:
        failures.append("runtime privilege hardening is incomplete")
    return failures
