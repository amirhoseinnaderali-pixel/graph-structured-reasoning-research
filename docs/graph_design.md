# Graph Design

The primary graph is a threshold graph over normalized candidate representations with cosine similarity threshold 0.75 and weighted edges. The primary score is weighted degree.

The ablation grid contains 16 conditions:

- builders: threshold and k-nearest-neighbor (k=3)
- edge modes: weighted and unweighted
- scoring: weighted degree, degree centrality, PageRank, and local neighborhood agreement

Graph configuration hashes are stored with results. Nodes are the exact frozen candidate IDs, and graph construction consumes only the shared representation similarity matrix. No test execution result is an input to graph construction or scoring.

The same candidate set is used for non-graph similarity ranking and every graph condition. This keeps graph modeling as the manipulated factor rather than candidate generation.