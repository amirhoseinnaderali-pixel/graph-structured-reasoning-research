#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, statistics
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from graph_reasoning_research.evaluation.metrics import bootstrap_ci, paired_difference_ci

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    groups=defaultdict(list)
    by_task_seed=defaultdict(dict)
    rows=[json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in rows:
        if row.get("status")=="INFRASTRUCTURE_ERROR":
            continue
        method=row["aggregation_method"]
        groups[method].append(row)
        by_task_seed[(row["task_id"],row["seed"])][method]=row

    summary={"experiment_id":rows[0]["experiment_id"] if rows else None,
             "candidate_set_hashes":sorted({r["candidate_set_hash"] for r in rows}),
             "methods":{}}
    for method,items in sorted(groups.items()):
        solved=[r["objective_result"]=="PASS" for r in items]
        lat=[float(r["aggregation_latency_ms"]) for r in items]
        summary["methods"][method]={
            "task_seed_n":len(items),
            "hidden_solved_rate":sum(solved)/len(solved) if solved else None,
            "bootstrap_ci":bootstrap_ci([float(x) for x in solved]) if solved else None,
            "mean_aggregation_latency_ms":statistics.mean(lat) if lat else None,
            "median_aggregation_latency_ms":statistics.median(lat) if lat else None,
            "mean_candidate_count":statistics.mean([r["budget"]["candidate_count"] for r in items]) if items else None,
            "model_calls":sum(r["generation_calls"] for r in items),
            "representation_calls":sum(r["representation_calls"] for r in items),
            "visible_verification_executions":sum(r["budget"]["visible_verification_executions"] for r in items),
            "graph_construction_ms":sum(r["graph_construction_latency_ms"] for r in items),
            "graph_density_mean":statistics.mean([r["graph_stats"]["density"] for r in items]) if any(r.get("graph_stats") for r in items) else None,
            "failure_classes":dict(sorted({fc:sum(1 for r in items if r.get("failure_class")==fc) for fc in {r.get("failure_class") for r in items if r.get("failure_class")}}.items())),
        }

    if "similarity_ranking" in groups:
        paired={}
        for method in sorted(groups):
            if method=="similarity_ranking":
                continue
            pairs=[]
            for key,methods in by_task_seed.items():
                if method in methods and "similarity_ranking" in methods:
                    pairs.append((float(methods[method]["objective_result"]=="PASS"),
                                   float(methods["similarity_ranking"]["objective_result"]=="PASS")))
            if pairs:
                paired[method]={
                    "n":len(pairs),
                    "paired_mean_difference":sum(a-b for a,b in pairs)/len(pairs),
                    "difference_bootstrap_ci":paired_difference_ci([a for a,_ in pairs],[b for _,b in pairs]),
                }
        summary["paired_vs_similarity"]=paired

    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")

if __name__=="__main__": main()
