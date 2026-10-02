#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from benchmarks.loaders.manifest import load_manifest
from graph_reasoning_research.experiments.config import load_yaml, validate_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    args = parser.parse_args()
    config = load_yaml(ROOT / args.config)
    blockers = validate_config(config)
    models = load_yaml(ROOT / config["candidate_generator_config"])
    representation = load_yaml(ROOT / config["representation_config"])
    graph = load_yaml(ROOT / config["graph_config"])
    runtime = load_yaml(ROOT / config["runtime_config"])
    pricing = load_yaml(ROOT / config["pricing_config"])

    try:
        manifest = load_manifest(ROOT / config["benchmark_manifest"], require_frozen=True)
    except Exception as exc:
        blockers.append(f"benchmark freeze: {exc}")
    if models.get("status") != "FROZEN":
        blockers.append("candidate generation model configuration is not FROZEN")
    if representation.get("status") != "FROZEN":
        blockers.append("embedding/representation configuration is not FROZEN")
    if graph.get("status") != "FROZEN":
        blockers.append("graph configuration is not FROZEN")
    if pricing.get("status") not in {"FROZEN", "UNAVAILABLE"}:
        blockers.append("pricing configuration must be FROZEN or explicitly UNAVAILABLE")
    if runtime.get("status") != "FROZEN" or not str(runtime.get("docker_image", "")).startswith("sha256:"):
        blockers.append("Docker image digest is not FROZEN")
    credential_env = models.get("candidate_generator", {}).get("credential_env")
    if not credential_env or not os.environ.get(credential_env):
        blockers.append("model credentials are unavailable")
    if not shutil.which("docker"):
        blockers.append("Docker CLI/daemon is unavailable")

    if blockers:
        print("NOT READY")
        for blocker in blockers:
            print(f"- {blocker}")
        return 1
    print("READY FOR EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
