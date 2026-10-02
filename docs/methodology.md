# Methodology

## Controlled pipeline

```text
problem
  -> fixed candidate generator
  -> N frozen candidate trajectories
  -> representation layer
  -> similarity matrix
  -> aggregation / selection
  -> objective evaluation
```

For the primary comparison, the candidate set, candidate order, representation process, seed, and candidate-generation budget are held fixed. Only the aggregation/selection rule changes.

## Conditions

- C0: first/single candidate reference.
- C1: independent candidate set with deterministic random/first analyses.
- C2: consensus where an answer-level consensus target is semantically appropriate.
- C3: similarity ranking using aggregate pairwise similarity without a graph object.
- C4: graph aggregation.
- C5: graph prioritization followed by an independent objective verifier.
- C6: graph ablations across builders, edge modes, and scoring functions.

No condition is assumed superior.

## Representation layer

Text, structured reasoning (where task material supports it), embeddings, and the similarity matrix are first-class artifacts. The embedding backend and revision are explicit configuration rather than hidden implementation constants.

## Independence

Selection-visible information is separated from hidden evaluation. Hidden tests are evaluation-only and cannot enter embeddings, graph edges, weights, centrality, ranking, or selection.
