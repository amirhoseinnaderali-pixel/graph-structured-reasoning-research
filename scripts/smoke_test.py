#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from graph_reasoning_research.experiments.config import load_yaml
from graph_reasoning_research.experiments.runner import run_real

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/experiments/EXP-001.yaml")
    args=parser.parse_args()
    config=load_yaml(ROOT/args.config)
    preflight=subprocess.run([sys.executable,str(ROOT/"scripts/preflight.py"),"--config",args.config],text=True)
    if preflight.returncode!=0:
        print("EXECUTION_SMOKE_TEST BLOCKED: preflight is not ready.")
        return 1
    try:
        path=run_real(ROOT,config,smoke=True)
    except Exception as exc:
        print(f"EXECUTION_SMOKE_TEST FAILED CLOSED: {type(exc).__name__}: {exc}")
        return 2
    print(f"EXECUTION_SMOKE_TEST PASSED: {path}")
    print("This artifact is validation-only and does not count as EXP-001 evidence.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
