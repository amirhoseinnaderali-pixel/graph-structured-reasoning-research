# Graph Design

## Builders

### Threshold

Edge `(i,j)` exists when cosine similarity is at least `tau`.

### k-nearest-neighbor

Each candidate connects to its configured `k` nearest peers; the implementation materializes the union of directed neighbor choices as an undirected candidate graph.

## Edge modes

Weighted edges retain the similarity value. Unweighted edges retain topology only.

## Scoring

The framework supports weighted degree, degree centrality, PageRank, and local neighborhood agreement. Scores are ranking signals only; they are not correctness probabilities.

## Complexity accounting

Representation, dense similarity, graph construction, and scoring are measured as aggregation-side costs. Candidate generation and objective verification are accounted for separately.
