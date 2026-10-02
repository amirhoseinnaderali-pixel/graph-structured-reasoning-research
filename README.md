# Graph-Structured Reasoning Research

Project 4 is a controlled research instrument for:

> Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve final candidate selection compared with simpler aggregation methods, under the same candidate set?

## EXP-001 scientific contract

frozen task → one real candidate-generation call → frozen candidate set + candidate_set_hash → one deterministic representation artifact + representation_hash → C0/C1/C2/C3/C4/C5/C6 → selection → independent hidden evaluation only after selection.

C0 is first candidate, C1 seeded random, C2 consensus, C3 direct similarity ranking, C4 primary graph aggregation, C5 graph-derived shortlist plus independent visible verification, and C6 graph ablations over builder × edge weighting × scoring method.

All methods consume the same frozen candidate set and the same representation artifact. Hidden tests never enter candidate generation, representation, similarity, graph construction, graph scoring, or selection.

## Frozen EXP-001 inputs

The benchmark is a provenance-locked 12-task subset of the frozen Project-3 HumanEval-derived benchmark, selected as the first eligible source-order task for each frozen category. Each task carries stable task, visible-test, hidden-test, and source-provenance hashes.

Candidate generation is frozen to gpt-4.1-mini-2025-04-14 with an explicit seeded request policy. Representation is a deterministic local SHA-256 feature-hashing + TF-IDF method. The graph contract freezes threshold and kNN construction, weighted and unweighted edges, and four graph scoring methods.

The runtime is pinned to a linux/amd64 Docker image digest with network isolation, read-only root, dropped capabilities, no-new-privileges, PID/CPU/memory limits, and a bounded timeout.

## Status

| State | Meaning |
|---|---|
| IMPLEMENTED | Real generator, representation, graph, verifier, budgets, runner, result schema, preflight, and smoke path are implemented. |
| VALIDATED | Automated tests and mock validation pass. |
| SCIENTIFICALLY AUDITED | Frozen inputs, hashes, hidden-test isolation, result schema, and budget/runtime gates pass audit. |
| READY FOR REAL EXECUTION | Code/config contracts are frozen; the actual environment must still pass real preflight. |
| REAL SMOKE PASSED | A separate EXECUTION_SMOKE_TEST artifact exists; it is validation-only. |
| EXP-001 EXECUTED | Only a real full run with immutable raw artifacts earns this state. |

Current Project-4 claim: the repository contains the real execution path and frozen EXP-001 protocol. EXP-001 has not been executed and no empirical result is reported.

## Validation commands

    python -m pytest -q
    python scripts/validate_config.py
    python scripts/scientific_audit.py
    python scripts/preflight.py
    python scripts/run_experiment.py --mode mock
    python scripts/smoke_test.py
    python scripts/run_experiment.py --mode real

Mock mode is validation-only. Real mode is fail-closed and will not start generation unless preflight succeeds.
