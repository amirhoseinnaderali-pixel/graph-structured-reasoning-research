# Reproducibility

Every real run records the experiment ID, run ID, Git SHA, configuration hash, benchmark hash, task ID, candidate-generator model and seed, generation configuration hash, embedding model/version, representation configuration hash, graph configuration hash, budget, token counts, latency, graph statistics, candidate-set hash, and evaluator result.

All stochastic components require explicit seeds. Candidate outputs are hashed before aggregation. Every aggregation condition records the same `candidate_set_hash`; the software provides an assertion that raises on candidate-set mismatch.

The EXP-001 benchmark manifest is **FROZEN** for the completed controlled study. Candidate-set hashing, representation/config hashing, and hidden-test isolation are part of the recorded protocol. The real execution path remains fail-closed for future reruns if the frozen material cannot be verified.
