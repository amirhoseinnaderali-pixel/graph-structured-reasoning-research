# Implementation Status

## State machine

1. IMPLEMENTED — execution architecture and scientific controls exist in source.
2. VALIDATED — automated tests and mock path pass.
3. SCIENTIFICALLY AUDITED — frozen inputs, hashes, hidden-test isolation, result schema, and budget/runtime gates pass audit.
4. READY FOR REAL EXECUTION — the repository can launch the real model/runtime path after environment preflight.
5. REAL SMOKE PASSED — one frozen task/seed completes the genuine model → representation → graph → visible/hidden verifier path; artifact is validation-only.
6. EXP-001 EXECUTED — all frozen EXP-001 tasks/seeds complete and immutable raw results exist.

The repository must never collapse these states into complete.

## Current implementation

- Frozen 12-task benchmark with source, task, visible-test, hidden-test, and materialization hashes.
- Frozen candidate generator and deterministic local representation.
- Candidate-set hash enforced once per task/seed and reused by all conditions.
- Shared representation artifact reused by similarity and graph conditions.
- Hidden tests are attached only to verifier inputs after selection.
- Primary C0-C5 conditions and a 16-cell C6 graph ablation factorial are implemented.
- Docker verifier is pinned and hardened.
- Budget counters are checked before generation, representation, verification, and graph operations.
- Real and mock adapters are explicitly separated.
- Raw result artifacts use exclusive file creation and include environment/config/benchmark hashes.
- Real smoke artifacts are stored separately under results/smoke_test/.

## External environment gates

The repository cannot claim a real smoke or EXP-001 run until the actual environment has OPENAI_API_KEY, a reachable Docker daemon, access to the pinned runtime image, and access to the configured model API.

Failure of any of these gates must stop the run before candidate generation.
