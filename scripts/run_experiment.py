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
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/experiments/EXP-001.yaml")
    ap.add_argument("--mode", choices=["mock", "real"], default="mock")
    args = ap.parse_args()
    cfg = load_yaml(ROOT / args.config)
    failures = validate_config(cfg)
    if failures:
        print("CONFIG INVALID")
        for f in failures: print(f"- {f}")
        return 1
    if args.mode == "real":
        print("REAL EXECUTION BLOCKED: EXP-001 is intentionally not executable in the initial state.")
        return 2
    out = ROOT / "results/validation/EXP-001-mock.jsonl"
    out.unlink(missing_ok=True)
    rows = run_mock(cfg, out)
    print(json.dumps({"status": "validation_only", "records": len(rows), "path": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
