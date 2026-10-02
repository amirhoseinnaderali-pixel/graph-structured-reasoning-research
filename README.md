# Graph-Structured Reasoning Research

Controlled research infrastructure for **Project 4** in a broader reasoning research program.

## Scientific question

> **Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve final candidate selection compared with simpler aggregation methods?**

The repository is deliberately neutral. It does not assume that graph aggregation helps. Results may show an improvement, no measurable benefit, benefits only for some candidate diversity or compute regimes, or insufficient value relative to its extra cost.

## EXP-001 — Controlled Graph Aggregation Benchmark

The primary experiment holds the candidate set fixed and varies only the aggregation/selection mechanism:

- **C0** — Single candidate
- **C1** — Independent candidates (candidate-set construction; selection is deterministic first/random analyses)
- **C2** — Majority / consensus
- **C3** — Similarity ranking
- **C4** — Graph aggregation
- **C5** — Graph + independent objective verification
- **C6** — Graph-construction/scoring ablations

The central scientific comparison is:

```text
same candidate set + same representation inputs
                 |
       +---------+---------+
       |                   |
 similarity ranking    graph ranking
       |                   |
       +---------+---------+
                 |
       objective correctness
```

## Status

**IMPLEMENTED / SCIENTIFICALLY AUDITED / NOT EXECUTED.**

The mock end-to-end pipeline is executable locally and is explicitly marked `validation_only`. Real EXP-001 is fail-closed until the benchmark, model configuration, embedding model, execution environment, and credentials are frozen and the readiness audit passes.

No empirical graph advantage, statistical significance, or benchmark performance is claimed by this repository.

## Quick validation

```bash
python -m pytest -q
make mock
make audit
```

`make audit` is expected to fail closed for a fresh checkout because the real benchmark and runtime inputs are intentionally not frozen.

## Real execution gate

The real runner refuses to execute while any of the following remains unresolved:

- frozen benchmark manifest with task/test hashes;
- frozen candidate-generator/model configuration;
- frozen embedding configuration;
- Docker runtime and pinned execution image digest;
- credentials for any external inference provider;
- scientific invariant audit.

See `docs/methodology.md`, `docs/reproducibility.md`, and `docs/experiment_registry.md`.
