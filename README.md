# Graph-Structured Reasoning Research

Project 4 is a controlled research instrument for one question:

> **Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve final candidate selection compared with simpler aggregation methods, under the same candidate set?**

## Scientific design

```text
same candidate set
      ↓
explicit representation + similarity
      ↓
different aggregation mechanism
      ↓
objective correctness + aggregation compute
```

EXP-001 implements C0 first candidate, C1 seeded random, C2 consensus, C3 similarity ranking, C4 graph aggregation, C5 graph + independent objective verification, and C6 graph ablations. Candidate-set hashing is an enforced invariant. Graph and similarity conditions share the same representation artifact in direct comparisons.

## Current status

**IMPLEMENTED / SCIENTIFICALLY AUDITED / NOT EXECUTED**

The repository is blocked from real execution because the benchmark is not frozen, exact generation/embedding models are not frozen, the Docker image digest is not frozen, model credentials are unavailable, and Docker availability has not been verified. Monetary pricing is explicitly marked unavailable rather than fabricated.

The mock pipeline is validation-only. Mock outputs are never scientific evidence.

## Validation

```bash
python -m pytest -q
python scripts/validate_config.py
python scripts/preflight.py
python scripts/scientific_audit.py
python scripts/run_experiment.py --mode mock
```

The full EXP-001 is intentionally **NOT EXECUTED** in the current project state.
