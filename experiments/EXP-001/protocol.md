# EXP-001 Protocol

1. Freeze benchmark task/test material and hashes.
2. Freeze candidate-generator model/version and generation parameters.
3. Freeze embedding model/version and representation configuration.
4. Freeze Docker image digest and visible/hidden test policy.
5. Run scientific audit.
6. Generate candidate sets once per task-seed pair.
7. Persist candidate-set hash before selection.
8. Run all aggregation conditions against that same candidate set.
9. Evaluate selected candidates with independent objective verification.
10. Preserve all candidate-level decision records and failures.
11. Only then compute aggregate statistics and figures.
