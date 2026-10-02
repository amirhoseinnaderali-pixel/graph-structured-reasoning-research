# Methodology

EXP-001 uses the same candidate set for every aggregation condition within each task/seed. Candidate generation is performed once, the resulting candidate set receives a deterministic candidate-set hash, and a single frozen representation artifact is reused by C0-C6.

The frozen benchmark is a 12-task stratified subset of the Project-3 HumanEval-derived benchmark family: the first eligible source-order task for each of 12 categories. The materialized task file and every task/test split are hash-locked.

C0 selects the first candidate. C1 uses seeded random selection. C2 uses the existing answer-consensus mechanism. C3 ranks directly by cosine similarity on the shared representation. C4 uses the primary threshold graph with weighted edges and weighted-degree scoring. C5 ranks candidates through the graph first, then applies visible objective verification to at most the frozen two-candidate shortlist. C6 enumerates threshold/kNN × weighted/unweighted × four frozen graph scoring functions.

Hidden tests are structurally unavailable to candidate generation, representation, similarity, consensus, graph construction, graph scoring, and selection. Hidden evaluation happens only after a strategy has selected one candidate.

The real execution environment uses the frozen linux/amd64 Docker digest and no network inside the candidate verifier. Budget counters are reserved before the corresponding operations and budget violations fail closed.