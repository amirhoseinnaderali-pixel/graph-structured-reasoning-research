# Prior Work Traceability

This repository is a new implementation and must not be treated as a copy of earlier projects.

## `graph_reasoning`

**Reused concept:** candidate-level graph aggregation based on relationships among reasoning trajectories and semantic similarity.

**New implementation:** a modular representation → similarity → graph → scoring → selection stack with explicit condition boundaries, candidate-set hashing, leakage invariants, result-schema validation, budget ledgers, and a direct similarity-ranking control.

**Previous limitation addressed:** earlier graph-oriented exploration mixed exploratory graph artifacts and research framing. This project makes the controlled aggregation comparison the primary scientific object and treats graph statistics as descriptive unless tied to objective outcomes.

## `efficient-reasoning-research`

**Reused concept:** explicit budget accounting, fail-closed execution gates, objective evaluation, and separation of visible selection from hidden final scoring.

**New implementation:** these controls are specialized for graph aggregation and for proving that graph-side computation is not silently free.

## `multi-model-reasoning-research`

**Reused concept:** same-input fairness, frozen candidate artifacts, explicit seeds, objective verifier independence, and validation-only mock runs.

**New implementation:** candidate generation is fully separated from aggregation so graph and non-graph conditions consume the identical candidate-set hash.

Parts of this repository are exploratory software infrastructure; they are not empirical findings.
