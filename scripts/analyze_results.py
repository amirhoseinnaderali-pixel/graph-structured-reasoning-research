#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from graph_reasoning_research.evaluation.metrics import accuracy, bootstrap_ci


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input", required=True); ap.add_argument("--output", required=True); args=ap.parse_args()
    groups=defaultdict(list)
    for line in Path(args.input).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        r=json.loads(line); groups[r["aggregation_method"]].append(r["objective_result"]=="PASS")
    out={}
    for m,vals in groups.items(): out[m]={"n":len(vals),"accuracy":accuracy(vals),"bootstrap_ci":bootstrap_ci([float(x) for x in vals])}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")

if __name__=="__main__": main()
