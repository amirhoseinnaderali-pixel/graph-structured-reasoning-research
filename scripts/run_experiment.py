#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_reasoning_research.experiments.config import load_yaml, validate_config
from graph_reasoning_research.experiments.runner import run_mock


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    args = parser.parse_args()
    config = load_yaml(ROOT / args.config)
    failures = validate_config(config)
    if failures:
        print("CONFIG INVALID")
        for failure in failures:
            print(f"- {failure}")
        return 1
    if args.mode == "real":
        print("REAL EXECUTION BLOCKED: run scripts/preflight.py first; EXP-001 remains NOT EXECUTED.")
        return 2
    output = ROOT / "results/validation/EXP-001-mock.jsonl"
    output.unlink(missing_ok=True)
    rows = run_mock(config, output)
    print(json.dumps({"status": "validation_only", "records": len(rows), "path": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
