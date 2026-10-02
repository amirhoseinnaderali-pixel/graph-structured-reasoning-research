#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from benchmarks.loaders.manifest import load_manifest, manifest_hash
from graph_reasoning_research.experiments.config import load_yaml, validate_config
from graph_reasoning_research.logging.schema import REQUIRED_FIELDS


def git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    args = parser.parse_args()
    failures: list[str] = []

    config = load_yaml(ROOT / args.config)
    failures.extend(validate_config(config))
    baseline_names = set(config.get("primary_baselines", []))
    for required_baseline in ("first_candidate", "random_candidate", "consensus", "similarity_ranking", "objective_verification"):
        if required_baseline not in baseline_names:
            failures.append(f"baseline fairness: missing {required_baseline}")

    if config.get("candidate_count", 0) < 2:
        failures.append("candidate equivalence: candidate_count must be >= 2")
    controls = config.get("scientific_controls", {})
    for control in ("candidate_set_hashing", "hidden_test_isolation", "representation_hashing", "graph_config_hashing"):
        if controls.get(control) is not True:
            failures.append(f"scientific controls: {control} is not enabled")

    models = load_yaml(ROOT / config["candidate_generator_config"])
    representation = load_yaml(ROOT / config["representation_config"])
    graph = load_yaml(ROOT / config["graph_config"])
    runtime = load_yaml(ROOT / config["runtime_config"])
    pricing = load_yaml(ROOT / config["pricing_config"])

    if models.get("status") != "FROZEN":
        failures.append("candidate-generator/model config is not FROZEN")
    for key in ("model_id", "model_revision", "credential_env"):
        if not models.get("candidate_generator", {}).get(key):
            failures.append(f"candidate-generator/model config: missing {key}")

    if representation.get("status") != "FROZEN":
        failures.append("representation config is not FROZEN")
    for key in ("method", "model_id", "model_revision", "dimension", "normalize_embeddings", "similarity_function"):
        if key not in representation:
            failures.append(f"representation config: missing {key}")

    if graph.get("status") != "FROZEN":
        failures.append("graph config is not FROZEN")
    for section in ("threshold", "knn", "weighted", "unweighted", "scoring"):
        if section not in graph:
            failures.append(f"graph transparency: missing section {section}")

    if runtime.get("status") != "FROZEN" or not str(runtime.get("docker_image", "")).startswith("sha256:"):
        failures.append("runtime: immutable Docker image digest is not frozen")

    if pricing.get("status") not in {"FROZEN", "UNAVAILABLE"}:
        failures.append("pricing: status must be FROZEN or UNAVAILABLE")

    schema_fields = REQUIRED_FIELDS
    required_cost_terms = {
        "generation_input_tokens",
        "generation_output_tokens",
        "representation_tokens",
        "embedding_latency_ms",
        "similarity_latency_ms",
        "graph_construction_latency_ms",
        "graph_scoring_latency_ms",
        "visible_verification_latency_ms",
        "hidden_verification_latency_ms",
    }
    if not required_cost_terms.issubset(schema_fields):
        failures.append("cost accounting: result schema is incomplete")

    manifest_path = ROOT / config["benchmark_manifest"]
    try:
        manifest = load_manifest(manifest_path, require_frozen=True)
        if manifest["evaluation_policy"]["hidden_tests_allowed_during_selection"]:
            failures.append("no leakage: hidden tests are allowed during selection")
        if not manifest["evaluation_policy"]["verifier_independent_of_graph"]:
            failures.append("no leakage: verifier is not independent of graph")
        expected = manifest.get("manifest_hash")
        if expected and expected != manifest_hash(manifest):
            failures.append("benchmark hash mismatch")
    except Exception as exc:
        failures.append(f"benchmark gate: {exc}")

    credential_env = models.get("candidate_generator", {}).get("credential_env")
    if not credential_env or not os.environ.get(credential_env):
        failures.append("credentials: required model credential is not configured")

    if not shutil.which("docker"):
        failures.append("execution environment: Docker CLI is unavailable")

    report = {
        "git_sha": git_sha(),
        "benchmark": "FROZEN" if not any("benchmark" in x for x in failures) else "NOT_READY",
        "model": models.get("status"),
        "representation": representation.get("status"),
        "graph": graph.get("status"),
        "runtime": runtime.get("status"),
        "pricing": pricing.get("status"),
        "failure_count": len(failures),
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
