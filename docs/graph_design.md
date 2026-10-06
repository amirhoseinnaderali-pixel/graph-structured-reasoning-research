# Graph Design

Graph construction is a first-class, hashed configuration. EXP-001 supports threshold and k-nearest-neighbor graphs, weighted or unweighted edges, and weighted-degree, degree-centrality, PageRank, and local-neighborhood-agreement scoring.

A threshold graph includes edge `(i,j)` when cosine similarity is at least the configured threshold. A k-NN graph connects each node to its deterministic top-k neighbors and materializes the union as an undirected graph. Weighted edges retain cosine similarity; unweighted edges use unit weight.

Every graph run records graph method, full graph configuration, graph configuration hash, node count, edge count, density, construction latency, and scoring latency. Graph scores are ranking signals rather than correctness probabilities.
