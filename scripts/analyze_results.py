#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_reasoning_research.evaluation.metrics import accuracy, bootstrap_ci, paired_difference_ci


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    groups = defaultdict(list)
    by_task_seed = defaultdict(dict)
    for line in Path(args.input).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        groups[row["aggregation_method"]].append(row)
        by_task_seed[(row["task_id"], row["seed"])][row["aggregation_method"]] = row

    methods = sorted(groups)
    summary = {
        method: {
            "n": len(rows),
            "accuracy": accuracy([r["objective_result"] == "PASS" for r in rows]),
            "bootstrap_ci": bootstrap_ci([float(r["objective_result"] == "PASS") for r in rows]),
            "mean_aggregation_latency_ms": sum(r["aggregation_latency_ms"] for r in rows) / len(rows),
        }
        for method, rows in groups.items()
    }

    paired = {}
    if "similarity_ranking" in methods:
        for method in methods:
            if method == "similarity_ranking":
                continue
            pairs = [
                (
                    float(row.get(method, {}).get("objective_result") == "PASS"),
                    float(row.get("similarity_ranking", {}).get("objective_result") == "PASS"),
                )
                for row in by_task_seed.values()
                if method in row and "similarity_ranking" in row
            ]
            if pairs:
                paired[method] = {
                    "difference_bootstrap_ci": paired_difference_ci(
                        [x for x, _ in pairs],
                        [y for _, y in pairs],
                    )
                }

    summary["paired_vs_similarity"] = paired
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
