# Methodology

## Central comparison

```text
problem
  -> fixed candidate generator
  -> N frozen candidate trajectories
  -> explicit representation
  -> similarity matrix
  -> aggregation / selection
  -> objective evaluation
```

The same candidate set is consumed by every aggregation condition. Candidate generation is not rerun per condition. Each candidate carries a candidate ID, task ID, generator model ID, seed, generation configuration hash, and output hash; the ordered candidate manifest is hashed into `candidate_set_hash`. A comparison fails if candidate manifests differ.

## Conditions

- C0 — first candidate.
- C1 — seeded random candidate.
- C2 — consensus/majority.
- C3 — similarity ranking without graph construction.
- C4 — graph aggregation.
- C5 — graph prioritization followed by independent objective verification.
- C6 — graph-construction/scoring ablations.

Graph-vs-similarity comparisons use the same representations and the same similarity matrix.

## Hidden-test isolation

Hidden evaluation is isolated from all selection-visible computation. Regression tests mutate hidden metadata while holding candidate text and hashes fixed and assert that representation hashes, graph edges, graph scores, and selected candidates remain unchanged.

## Compute

Generation calls/tokens, representation calls/tokens/latency, similarity latency, graph construction, graph scoring, aggregation latency, visible verification, and hidden evaluation are separate result fields.
