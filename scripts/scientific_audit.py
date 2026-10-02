#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, platform, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks, manifest_hash
from graph_reasoning_research.experiments.config import config_hash, load_yaml, validate_bundle
from graph_reasoning_research.logging.schema import REQUIRED_FIELDS

def git_sha():
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    except Exception: return None

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/experiments/EXP-001.yaml")
    args=parser.parse_args()
    failures=[]
    config=load_yaml(ROOT/args.config)
    failures.extend(validate_bundle(ROOT,config))
    baseline_names=set(config.get("primary_baselines",[]))
    required=("first_candidate","random_candidate","consensus","similarity_ranking","objective_verification")
    for name in required:
        if name not in baseline_names: failures.append(f"baseline fairness: missing {name}")
    graph=config.get("primary_graph",{})
    if graph.get("builder")!="threshold" or graph.get("scoring")!="weighted_degree":
        failures.append("primary graph configuration is not the frozen threshold/weighted-degree condition")
    controls=config.get("scientific_controls",{})
    for control in ("candidate_set_hashing","hidden_test_isolation","representation_hashing","graph_config_hashing","single_candidate_generation_call_per_task_seed","hidden_evaluation_after_selection_only"):
        if controls.get(control) is not True: failures.append(f"scientific control disabled: {control}")
    manifest=None
    try:
        manifest=load_manifest(ROOT/config["benchmark_manifest"],require_frozen=True)
        load_materialized_tasks(ROOT/"benchmarks/programming/exp001_v1/tasks.jsonl",manifest)
        if manifest_hash(manifest)!=manifest["manifest_sha256"]: failures.append("benchmark manifest hash mismatch")
        if len(manifest["tasks"])!=12: failures.append("benchmark task count is not the frozen 12-task Project-4 subset")
        if any("hidden" in t["candidate_generation_prompt_view"].lower() for t in manifest["tasks"]): failures.append("hidden-test material appears in candidate prompts")
    except Exception as exc:
        failures.append(f"benchmark gate: {exc}")
    schema_required={"candidate_set_hash","representation_hash","benchmark_hash","status","generation","representation","aggregation","visible_evaluation","hidden_evaluation","budget","environment"}
    if not schema_required.issubset(REQUIRED_FIELDS): failures.append("result schema missing required scientific provenance fields")
    models=load_yaml(ROOT/config["candidate_generator_config"])
    rep=load_yaml(ROOT/config["representation_config"])
    runtime=load_yaml(ROOT/config["runtime_config"])
    cfg_hashes={"model":config_hash(models),"representation":config_hash(rep),"runtime":config_hash(runtime)}
    cred=models["candidate_generator"].get("credential_env")
    report={
        "git_sha":git_sha(),
        "benchmark_status":"FROZEN" if manifest and not any("benchmark" in x for x in failures) else "NOT_READY",
        "model_status":models.get("status"),
        "representation_status":rep.get("status"),
        "runtime_status":runtime.get("status"),
        "configuration_hashes":cfg_hashes,
        "docker_executable":bool(shutil.which("docker")),
        "credentials_configured":bool(cred and os.environ.get(cred)),
        "failure_count":len(failures),
        "failures":sorted(set(failures)),
    }
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if not failures else 1

if __name__=="__main__": raise SystemExit(main())
