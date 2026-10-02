# Reproducibility

Every real EXP-001 invocation receives a unique run ID. Raw result artifacts use exclusive creation and therefore cannot overwrite an earlier run.

The benchmark manifest is hash-locked and its 12 tasks are materialized from the frozen Project-3 HumanEval-derived benchmark family. Each task contains a stable task hash plus independent visible and hidden test hashes. The materialized benchmark file has its own SHA-256.

Candidate generation records model ID/revision, seed, generation configuration hash, token counts, retry policy, and output hashes. The candidate-set manifest is hashed before aggregation.

Representation is generated exactly once for each task/seed candidate set and reused by all similarity/graph conditions. The representation configuration and representation artifact are hashed.

Every result records Git SHA, benchmark hash, model metadata, representation metadata, graph configuration hash, budget counters, timing, candidate-set hash, selection metadata, visible evaluation metadata, and hidden evaluation metadata.

The runtime configuration is digest-pinned and records platform and sandbox restrictions. Preflight verifies the benchmark, materialization, frozen configs, credential availability, and Docker daemon before a real run starts.

Mock execution is validation-only. Smoke execution is labeled EXECUTION_SMOKE_TEST and stored separately; it is not EXP-001 evidence.
