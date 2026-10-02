# Historical Experiment Summary

This table contains only historical empirical evidence that is supported by preserved artifacts. Missing correctness/runtime fields are intentionally left as **not measured** rather than inferred.

## Conditions and evidence

| Condition | Actual implementation/config | Tasks | Seeds | Candidate count | Result artifact | Evidence level |
| --- | --- | --- | --- | --- | --- | --- |
| Historical graph-of-thoughts | `graph_reasoning/legacy/graph.py`; threshold 0.6; top-k 3; Louvain seed 42; resolution 1.2 | 1 hard-coded LTI signal-processing problem | No task-level seed record | 17 stored solution instances | `artifacts/historical/got_data.json`, `got_graph.gexf`, PNGs | RAW_EXECUTION_EVIDENCE / HISTORICAL_EXPLORATORY |
| Historical chunk graph | `graph_reasoning/legacy/reasoning_graph.py`; chunk size 300; threshold 0.5; top-k 5; Louvain seed 42; resolution 1.0 | Same historical problem | No task-level seed record | 3 solution/strategy sources; 22 chunks | `improved_data.json`, `improved_graph.gexf`, `improved_similarity.npy`, PNG | RAW_EXECUTION_EVIDENCE / HISTORICAL_EXPLORATORY |
| PageRank / eigenvector | `graph_reasoning/legacy/page_rank.py`; answer similarity graph; PageRank damping 0.85 | Intended ranking stage | Not recorded | Not preserved in result record | No saved ranking output | DOCUMENTATION_ONLY for empirical claims |
| K-Means / clustering | `graph_reasoning/legacy/k_means.py`; centroid representatives; cluster-size/coherence ranking | Intended ranking stage | Not recorded | Not preserved in result record | No saved ranking output | DOCUMENTATION_ONLY for empirical claims |
| A1–A10 graph ablations | `configs/ablation.yaml`, `docs/ablation_plan.md` | Planned controlled evaluation | Config seed 42 | Planned fixed candidate set | No result artifacts | DOCUMENTATION_ONLY |
| Hardened Project-4 EXP-001 | Current target repo; main = NOT_EXECUTED; project4 branch = READY_FOR_REAL_EXECUTION | Controlled benchmark design | 42, 43, 44 | 5 candidates | No empirical EXP-001 results | VALIDATION_ONLY / DOCUMENTATION_ONLY |

## Historical results

| Method / artifact | Tasks | Solved | Success Rate | Candidate / source count | Runtime | Observed result |
| --- | --- | --- | --- | --- | --- | --- |
| Graph-of-thoughts | 1 | Not measured | Not measured | 17 solutions | Not preserved | 230 nodes; 1,339 edges; 842 similarity; 268 dependency; 229 hierarchy; 10 communities |
| Chunk-level graph | 1 | Not measured | Not measured | 3 solution/strategy sources; 22 chunks | Not preserved | 45 nodes; 67 edges; 23 similarity edges; 7 communities; reported mean similarity 0.7766983146252839 |
| PageRank / eigenvector | 1 intended | Not reportable | Not reportable | Not preserved | Not preserved | No selected-candidate/correctness record found |
| K-Means / clustering | 1 intended | Not reportable | Not reportable | Not preserved | Not preserved | No selected-candidate/correctness record found |

## Recomputed checks

| Check | Result | Source |
| --- | --- | --- |
| `got_data.json` node count vs `got_graph.gexf` | 230 vs 230 | Raw JSON + GEXF |
| `got_data.json` edge count vs `got_graph.gexf` | 1,339 vs 1,339 | Raw JSON + GEXF |
| `improved_data.json` node count vs `improved_graph.gexf` | 45 vs 45 | Raw JSON + GEXF |
| `improved_data.json` edge count vs `improved_graph.gexf` | 67 vs 67 | Raw JSON + GEXF |
| Graph-of-thoughts mixed communities | 10 / 10 = 1.0000 | Recomputed from `got_data.json` |
| Chunk-graph mixed communities | 2 / 7 = 0.2857 | Recomputed from `improved_data.json` |

## Fairness boundary

The historical artifacts do not provide a candidate-set hash or condition-level manifest. Therefore same-candidate-set equivalence between graph ranking and non-graph baselines is **not established**.

## Evaluation boundary

No hidden tests, visible tests, objective execution verifier, or standardized correctness labels are preserved for the historical run. The reported numbers are graph-structure measurements, not task success measurements.
