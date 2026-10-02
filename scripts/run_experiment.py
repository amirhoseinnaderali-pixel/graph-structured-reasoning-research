#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from graph_reasoning_research.experiments.config import load_yaml, validate_config
from graph_reasoning_research.experiments.runner import run_mock, run_real

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/experiments/EXP-001.yaml")
    parser.add_argument("--mode",choices=["mock","real"],default="mock")
    args=parser.parse_args()
    config=load_yaml(ROOT/args.config)
    failures=validate_config(config)
    if args.mode=="mock":
        if failures:
            print("CONFIG INVALID")
            for failure in failures: print(f"- {failure}")
            return 1
        output=ROOT/"results/validation/EXP-001-mock.jsonl"
        output.unlink(missing_ok=True)
        rows=run_mock(config,output)
        print(json.dumps({"status":"validation_only","records":len(rows),"path":str(output)},indent=2))
        return 0
    preflight=subprocess.run([sys.executable,str(ROOT/"scripts/preflight.py"),"--config",args.config],text=True)
    if preflight.returncode!=0:
        print("REAL EXECUTION NOT STARTED: preflight failed.")
        return 2
    try:
        path=run_real(ROOT,config,smoke=False)
    except Exception as exc:
        run_id=uuid.uuid4().hex
        artifact=ROOT/"results/raw/EXP-001"/f"FAILED-{run_id}.json"
        artifact.parent.mkdir(parents=True,exist_ok=True)
        status="BUDGET_INELIGIBLE" if "budget_ineligibility" in str(exc) else "INFRASTRUCTURE_ERROR" if "verification infrastructure" in str(exc) or "preflight" in str(exc).lower() else "MODEL_OR_PIPELINE_FAILURE"
        with artifact.open("x",encoding="utf-8") as handle:
            json.dump({"experiment_id":"EXP-001","run_id":run_id,"status":status,"error":str(exc),"error_type":type(exc).__name__,"empirical_evidence":False},handle,indent=2,sort_keys=True)
        print(f"REAL EXECUTION FAILED CLOSED: {type(exc).__name__}: {exc}")
        print(f"Failure artifact: {artifact}")
        return 3
    print(json.dumps({"status":"EXECUTED","path":str(path)},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
