# Reproducibility

Every real run should record experiment ID, run ID, Git SHA, configuration hash, benchmark hash, task ID, candidate-generator configuration, embedding model/version, graph configuration, seed, budgets, token usage, latency, graph statistics, and evaluator result.

All stochastic components require explicit seeds. Result records are append-only JSONL with a schema version. Configuration and benchmark hashes are designed to make accidental drift visible.

The initial benchmark manifest is intentionally **UNFROZEN**. This makes real EXP-001 fail closed rather than silently run on mutable task material.
