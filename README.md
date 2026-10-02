# Graph-Structured Reasoning Research

### Portfolio status

**REGISTERED — HISTORICAL EXPLORATORY CASE STUDY**

The preserved historical graph_reasoning artifacts are sufficient to document graph construction, similarity/dependency structure, and community formation, but they do not establish downstream task-accuracy improvement or graph-selection superiority. The current hardened EXP-001 is a future instrument and is not claimed as executed.

Project 4 studies one focused question:

> **Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve final candidate selection compared with simpler aggregation methods, under the same candidate set?**

---

# Expected Hypothesis — Pre-Execution

> ⚠️ **HYPOTHESIS ONLY — NOT AN EMPIRICAL RESULT**
>
> The following section states the expected behavior of the frozen EXP-001 before the benchmark is executed. It is a falsifiable pre-data hypothesis, not a measured result, ranking, or performance claim.

## Hypothesized Result

We hypothesize that graph-based aggregation will provide a **modest but measurable improvement in candidate-selection accuracy** over simpler aggregation methods when generated reasoning trajectories contain complementary or partially conflicting information.

The expected pattern is that:

- **Consensus** should perform well when multiple candidates converge on the same correct reasoning.
- **Similarity-based ranking** should be effective when semantically similar solutions are also correct.
- **Graph-based aggregation** should become more useful when correctness depends on combining information across multiple trajectories, because the graph explicitly represents both semantic similarity and relational structure among candidate reasoning paths.

We therefore expect the primary graph condition — using a **similarity-threshold graph with weighted edges and weighted-degree scoring** — to outperform first-candidate and random selection, and potentially provide a small improvement over direct similarity ranking and consensus on heterogeneous tasks.

The expected improvement should be larger on tasks where correct solutions appear as **structurally connected reasoning patterns** rather than as repeated identical answers.

## Expected trade-off

The main anticipated trade-off is **computational overhead**.

Graph construction, embedding-based similarity computation, edge construction, and graph scoring introduce additional computation and latency relative to simpler aggregation methods.

The expected conclusion is therefore **not** that graph aggregation universally dominates every baseline.

Instead:

> **Graph aggregation may provide a better accuracy–compute trade-off on tasks with diverse reasoning trajectories, while offering less benefit when candidates are already highly redundant or nearly identical.**

## Expected ablation behavior

The ablation study is expected to show that performance depends on both **graph construction** and **graph scoring**.

We hypothesize that:

- **Weighted graphs** preserve useful similarity information better than unweighted graphs.
- **PageRank** and **local-neighborhood agreement** may behave differently depending on graph density and topology.
- **Similarity-threshold** and **k-nearest-neighbor** graph variants may produce different robustness profiles.
- Graph construction itself is therefore an important experimental factor, rather than a neutral preprocessing step.

These expectations are intentionally directional rather than numerical because the current repository does not contain a real EXP-001 result set.

## Anticipated mechanism

The hypothesized mechanism is:

```text
Multiple reasoning trajectories
            ↓
Semantic + relational structure
            ↓
Explicit reasoning graph
            ↓
Aggregation / centrality / neighborhood signals
            ↓
Better candidate selection
```

The strongest expected gains should occur when useful information is **distributed across different trajectories** rather than repeated verbatim.

## What would count as support?

A future real run would support the hypothesis if the graph condition:

1. receives the same frozen candidate set as the comparison methods;
2. improves objective candidate-selection accuracy on the held-out evaluation;
3. retains that advantage after the graph's additional compute is accounted for.

A result in which graph aggregation is no better than simpler methods, or where its compute overhead outweighs a small accuracy gain, would weaken the hypothesis.

A surprising result is therefore valid evidence; the hypothesis is not intended to be retrofitted after observing the data.

---

## Historical research case study

The repository now separates the **historical exploratory evidence** from the **current hardened experiment instrument**.

### What was actually executed historically

The related historical repository `amirhoseinnaderali-pixel/graph_reasoning` contains preserved outputs from the original multi-model reasoning pipeline:

- **17 stored solution instances** from **7 model identifiers**
- **212 thought nodes**
- **230 total graph nodes**
- **1,339 total graph edges**
- **842 similarity edges**
- **268 dependency edges**
- **10 detected communities**
- a second chunk-level artifact with **45 nodes, 67 edges, 22 chunks, 23 similarity edges, and 7 communities**

These are **graph-structure observations**, not task-accuracy results.

The historical source implements graph-of-thoughts construction, semantic-similarity edges, dependency edges, community detection, PageRank/eigenvector ranking, and clustering. However, no preserved condition-level ranking outputs or correctness records establish that any of those selectors improved task performance.

### Main historical finding

The strongest supported observation is that the historical graph construction produced nontrivial cross-solution structure: all 10 graph-of-thoughts communities contained nodes from more than one solution source. In the smaller chunk graph, 2 of 7 communities mixed multiple sources.

This shows that graph structure can expose relationships among generated reasoning traces. It does **not** show that those relationships improve candidate selection or correctness.

### Conclusion

The historical evidence supports a **graph-construction / exploratory reasoning study**, not a controlled performance claim.

> **Historical experiments demonstrate nontrivial graph structure over multiple reasoning trajectories, but they do not demonstrate improved task accuracy or candidate-selection quality over simpler aggregation.**

See the full evidence audit and traceability tables:

- [Historical research report](docs/research_report.md)
- [Historical result tables](results/tables/historical_experiment_summary.md)

## Current hardened Project-4 instrument

The current repository contains a controlled EXP-001 design with candidate-set hashing, representation/configuration hashing, hidden-test isolation, independent objective-verification interfaces, and graph ablations.

**Current status: IMPLEMENTED / SCIENTIFICALLY AUDITED / NOT EXECUTED**

The mock pipeline is validation-only. Mock outputs are never treated as scientific evidence.

The `project4/exp001-real-execution` branch contains the hardened real-run configuration, but it is **not historical evidence** and is not claimed as executed.

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

The intended EXP-001 conditions include first-candidate, seeded random, consensus, similarity ranking, graph aggregation, graph + independent objective verification, and graph-construction/scoring ablations.

Candidate-set hashing is an enforced invariant in the hardened instrument.

## Evidence policy

The project distinguishes:

- `RAW_EXECUTION_EVIDENCE`
- `DERIVED_FROM_RAW_RESULTS`
- `HISTORICAL_EXPLORATORY`
- `VALIDATION_ONLY`
- `DOCUMENTATION_ONLY`

No mock output, smoke test, configuration check, or documentation claim is presented as empirical task performance.

## Validation

```bash
python -m pytest -q
python scripts/validate_config.py
python scripts/preflight.py
python scripts/scientific_audit.py
python scripts/run_experiment.py --mode mock
```

These checks validate the research instrument. They do not substitute for a real EXP-001 execution.
