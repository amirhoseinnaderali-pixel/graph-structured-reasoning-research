#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from benchmarks.loaders.manifest import load_manifest
from graph_reasoning_research.experiments.config import load_yaml, validate_config
from graph_reasoning_research.logging.schema import REQUIRED_FIELDS


def git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    args = ap.parse_args()
    failures: list[str] = []

    cfg = load_yaml(ROOT / args.config)
    failures.extend(validate_config(cfg))
    baseline_names = set(cfg.get("primary_baselines", []))
    if "similarity_ranking" not in baseline_names:
        failures.append("baseline fairness: similarity_ranking baseline is missing")
    if "first_candidate" not in baseline_names:
        failures.append("baseline fairness: first_candidate baseline is missing")
    if cfg.get("candidate_count", 0) < 2:
        failures.append("candidate equivalence: candidate_count must be >= 2")
    models = load_yaml(ROOT / cfg["candidate_generator_config"])
    if models.get("embedding", {}).get("normalize_embeddings") is not True:
        failures.append("representation consistency: embedding normalization policy is not explicit")
    if not models.get("embedding", {}).get("model_id"):
        failures.append("representation consistency: embedding model ID is missing")
    graph_cfg = load_yaml(ROOT / cfg["graph_config"])
    if graph_cfg.get("status") not in {"FROZEN", "FROZEN_FOR_SOFTWARE_VALIDATION"}:
        failures.append("graph transparency: graph config status is not frozen/validation-frozen")
    for section in ("threshold", "knn", "weighted", "unweighted", "scoring"):
        if section not in graph_cfg:
            failures.append(f"graph transparency: missing explicit config section '{section}'")
    if not graph_cfg.get("scoring", {}).get("methods"):
        failures.append("graph transparency: no graph scoring methods are configured")
    if sorted(cfg.get("seeds", [])) != cfg.get("seeds", []):
        failures.append("reproducibility: seeds must be in deterministic order")
    if not cfg.get("seeds"):
        failures.append("reproducibility: explicit seeds are missing")
    if not REQUIRED_FIELDS.issubset({
        "experiment_id", "run_id", "task_id", "seed", "aggregation_method",
        "representation_method", "candidate_id", "selected_candidate_id", "objective_result",
        "generation_tokens", "representation_tokens", "embedding_latency_ms", "similarity_latency_ms",
        "representation_latency_ms", "graph_construction_latency_ms", "graph_scoring_latency_ms",
        "aggregation_latency_ms", "verification_latency_ms", "candidate_set_hash", "representation_hash", "graph_stats"
    }):
        failures.append("reproducibility: result schema is incomplete")
    manifest_path = ROOT / cfg["benchmark_manifest"]
    try:
        manifest = load_manifest(manifest_path, require_frozen=True)
        if manifest["evaluation_policy"]["hidden_tests_allowed_during_selection"]:
            failures.append("no leakage: hidden tests are allowed during selection")
        if not manifest["evaluation_policy"]["verifier_independent_of_graph"]:
            failures.append("no leakage: verifier independence is not declared")
    except Exception as exc:
        failures.append(f"benchmark gate: {exc}")
    required_cost_terms = ["generation_tokens", "representation_latency_ms", "graph_construction_latency_ms", "graph_scoring_latency_ms", "aggregation_latency_ms", "verification_latency_ms"]
    if any(term not in REQUIRED_FIELDS for term in required_cost_terms):
        failures.append("cost accounting: schema does not expose all cost dimensions")
    if models.get("status") != "FROZEN":
        failures.append("candidate-generator/model config is not FROZEN")
    if models.get("embedding", {}).get("provider") == "UNSET":
        failures.append("embedding provider is UNSET")
    credential_env = models.get("candidate_generator", {}).get("credential_env", "UNSET")
    if credential_env in {None, "", "UNSET"}:
        failures.append("credentials: credential environment variable is not configured")
    elif not os.environ.get(credential_env):
        failures.append(f"credentials: {credential_env} is not present")
    if not shutil.which("docker"):
        failures.append("Docker CLI is not installed")
    print(f"GIT_SHA={git_sha() or 'UNKNOWN'}")
    print(f"REAL_EXECUTION_READY={not failures}")
    print(f"FAILURE_COUNT={len(failures)}")
    for failure in failures: print(f"NOT_READY: {failure}")
    return 0 if not failures else 1

if __name__ == "__main__": raise SystemExit(main())
