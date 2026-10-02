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

from graph_reasoning_research.experiments.config import load_yaml, validate_bundle


def docker_ready() -> tuple[bool, str]:
    docker = shutil.which("docker")
    if not docker:
        return False, "Docker CLI is unavailable"
    try:
        proc = subprocess.run(
            [docker, "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return False, "Docker daemon check timed out"
    if proc.returncode != 0:
        return False, f"Docker daemon is unreachable: {proc.stderr.strip()[:300]}"
    return True, f"Docker server {proc.stdout.strip()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    parser.add_argument("--skip-credentials", action="store_true")
    args = parser.parse_args()

    config = load_yaml(ROOT / args.config)
    blockers = validate_bundle(ROOT, config)

    model_cfg = load_yaml(ROOT / config["candidate_generator_config"])
    if model_cfg.get("candidate_generator", {}).get("provider") == "mock":
        blockers.append("real execution rejects mock candidate adapters")

    credential_env = model_cfg.get("candidate_generator", {}).get("credential_env")
    if not args.skip_credentials and (not credential_env or not os.environ.get(credential_env)):
        blockers.append("model credentials are unavailable")

    ready, docker_message = docker_ready()
    if not ready:
        blockers.append(docker_message)

    if blockers:
        print("NOT READY")
        for blocker in sorted(set(blockers)):
            print(f"- {blocker}")
        return 1

    print("READY FOR REAL EXECUTION")
    print(docker_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
