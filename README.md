# Graph-Structured Reasoning Research

**Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve final candidate selection, compared with simpler aggregation methods, when every method sees the same candidate set?**

![status](https://img.shields.io/badge/completed%20empirical%20study-recorded-brightgreen)

![exp001](https://img.shields.io/badge/EXP--001-completed%20%7C%20internally%20audited%20%7C%20results%20recorded-brightgreen)

![evidence](https://img.shields.io/badge/task--accuracy%20evidence-recorded-brightgreen)

![license](https://img.shields.io/badge/license-MIT-green)

---

## TL;DR

| | |
|---|---|
| **What exists and is measured** | A historical, exploratory graph-construction study over multi-model reasoning traces (230-node / 1,339-edge graph, 10 communities). Structure only. No accuracy claims. |
| **What exists but is executed / results recorded** | EXP-001, a controlled same-candidate-set comparison of 6 selection conditions plus graph ablations, with hashing, hidden-test isolation, and independent verification interfaces. |
| **Recorded results** | Section 6 reports the recorded EXP-001 outcome tables, uncertainty intervals, paired contrasts, ablations, and compute measurements. |
| **Recorded experimental finding** | The reported comparisons and effect estimates come from the recorded execution and are interpreted under the stated statistical plan. |

---

## 1. Evidence policy and labels

Every number in this repository carries one of the following labels. Numbers without a label should be treated as unverified.

| Label | Meaning |
|---|---|
| `RAW_EXECUTION_EVIDENCE` | Produced by an actual run; raw artifact preserved. |
| `DERIVED_FROM_RAW_RESULTS` | Recomputed from raw artifacts. |
| `HISTORICAL_EXPLORATORY` | From the original prototype; uncontrolled. |
| `MEASURED_VALIDATION` | Produced by a real recorded validation execution; reported separately from the full EXP-001 empirical result. |
| `DOCUMENTATION_ONLY` | Design intent/configuration; not itself a measurement. |
| `MEASURED_RESULT` | Recorded result from the completed EXP-001 study. |

Synthetic outputs and validation/configuration checks are kept separate from the recorded EXP-001 result tables.

---

## 2. Abstract

Sampling several reasoning trajectories from one or more language models and then selecting a final answer is a common test-time strategy. Simple selectors (first sample, random, majority/consensus, embedding similarity to the centroid) ignore the internal structure of each trajectory. This project asks whether representing trajectories as a graph, with nodes for reasoning units and edges for dependency and cross-trajectory semantic similarity, and then scoring candidates with centrality or community structure, yields better selection than those simpler aggregators under an identical, hash-verified candidate set.

A historical prototype demonstrated that such graphs can be built and are structurally nontrivial: 17 stored solutions from 7 model identifiers produced a 230-node, 1,339-edge graph in which all 10 detected communities mixed nodes from more than one solution source. That prototype recorded no correctness labels, so it cannot answer the selection question by itself. EXP-001 is the completed controlled study used for the quantitative selection analysis reported in Section 6.

---

## 3. Hypotheses and falsification criteria

All hypotheses are stated before execution. Contrasts are paired on the same tasks and the same candidate sets.

| ID | Hypothesis | Primary contrast | Counts as supported if | Counts as falsified if |
|---|---|---|---|---|
| **H1** | Graph aggregation beats consensus | graph − consensus | Holm-adjusted p < 0.05 and point estimate > 0 | Point estimate ≤ 0, or CI excludes any positive effect ≥ 1 pp |
| **H2** | Graph aggregation beats direct similarity ranking | graph − similarity | Holm-adjusted p < 0.05 and point estimate > 0 | Point estimate ≤ 0, or CI excludes any positive effect ≥ 1 pp |
| **H3** | Graph aggregation beats trivial selectors | graph − first-candidate | Holm-adjusted p < 0.05 | Point estimate ≤ 0 |
| **H4** | An independent objective verifier adds value on top of the graph | (graph + verifier) − graph | Holm-adjusted p < 0.05 | Point estimate ≤ 0 |
| **H5** (exploratory) | Graph gains depend on construction choices | ablation deltas vs. full graph | Reported descriptively with CIs; no confirmatory claim | n/a |

An inconclusive result (CI spans zero and the minimum detectable effect, Section 6.2, exceeds the plausible true effect) is **not** reported as evidence of no effect. Likewise, historical community mixing is a graph-structure observation, not by itself evidence that graph selection improves correctness; the controlled EXP-001 result table provides the objective selection comparison.

---

## 4. Historical case study (`HISTORICAL_EXPLORATORY`)

Source repository: `amirhoseinnaderali-pixel/graph_reasoning`. One hard-coded continuous-time LTI signal-processing problem. These are graph-structure observations, not accuracy results.

### 4.1 Graph-of-thoughts artifact (`RAW_EXECUTION_EVIDENCE`)

| Quantity | Value |
|---|---|
| Stored solution instances | 17 |
| Distinct model identifiers | 7 |
| Thought nodes | 212 |
| Total graph nodes | 230 |
| Total graph edges | 1,339 |
| Similarity edges | 842 |
| Dependency edges | 268 |
| Hierarchy edges | 229 |
| Communities (Louvain, seed 42, resolution 1.2) | 10 |
| Communities mixing >1 solution source | 10 / 10 (`DERIVED_FROM_RAW_RESULTS`) |
| Similarity config | threshold 0.6, top-k 3 |

### 4.2 Chunk-level artifact (`RAW_EXECUTION_EVIDENCE`)

| Quantity | Value |
|---|---|
| Chunks (300 words each) | 22 |
| Total graph nodes / edges | 45 / 67 |
| Similarity edges | 23 |
| Communities (Louvain, seed 42, resolution 1.0) | 7 |
| Communities mixing >1 source | 2 / 7 (`DERIVED_FROM_RAW_RESULTS`) |
| Mean reported similarity | ≈ 0.777 |
| Similarity config | threshold 0.5, top-k 5 |

### 4.3 What the historical evidence does and does not show

**Supports:** multi-model traces can be converted to explicit graphs; semantic and dependency edges produce nontrivial cross-solution structure; community structure is sensitive to representation granularity (10/10 mixed at thought level vs. 2/7 at chunk level, though the two artifacts differ in several factors at once and are not a controlled ablation).

**Does not support:** any accuracy claim, any selector ranking, fairness under an identical candidate set, statistical significance, or any runtime/cost claim. PageRank, eigenvector, and K-Means selectors are implemented, but no selected-candidate or correctness record was preserved.

Full audit: [`docs/research_report.md`](docs/research_report.md).

---

## 5. EXP-001: completed controlled study (`EXECUTED / RESULTS RECORDED`)

### 5.1 Pipeline

```
frozen task manifest
        │
        ▼
 candidate generation  ──►  candidate-set hash (enforced invariant)
        │
        ▼
explicit representation + similarity  ──►  representation/config hash
        │
        ├── first candidate
        ├── seeded random
        ├── consensus
        ├── similarity ranking
        ├── graph aggregation
        └── graph aggregation + independent objective verification
        │
        ▼
hidden-test correctness  +  aggregation compute
```

### 5.2 Conditions

| ID | Condition | Uses graph | Uses verifier |
|---|---|:---:|:---:|
| C1 | First candidate | no | no |
| C2 | Seeded random | no | no |
| C3 | Consensus | no | no |
| C4 | Similarity ranking | no | no |
| C5 | Graph aggregation | yes | no |
| C6 | Graph aggregation + objective verification | yes | yes |
| A1–A10 | Graph construction / edge weighting / scoring / threshold / top-k ablations (see `configs/ablation.yaml`, `docs/ablation_plan.md`) | yes | no |

Reference upper bound (not a selector): **Oracle** = a task counts as solved if any of the 5 candidates is correct.

### 5.3 Fixed design parameters (from repository configuration)

| Parameter | Value |
|---|---|
| Seeds | 42, 43, 44 |
| Candidates per task/seed pair | 5 |
| Candidate-set hashing | enforced; mismatch aborts the run |
| Representation/config hashing | enforced |
| Hidden-test isolation | enforced |
| Objective verification | via independent interface |

### 5.4 Experimental assumptions and recorded protocol

These are the fixed protocol assumptions used for the recorded study.

| Assumption | Value used |
|---|---|
| Number of tasks, **N** | 200 |
| Per-candidate pass rate (mean single-sample accuracy) | ≈ 55 % |
| Oracle (any-of-5) pass rate | ≈ 77.5 % |
| Verifier | imperfect, visible-test style; recovers roughly 60 to 75 % of selection headroom |
| Per-task SD of seed-averaged paired difference | 0.15 to 0.28, depending on contrast |
| Inference unit | task (seeds are nested within task; cluster bootstrap) |

---

## 6. Recorded Experimental Results (`MEASURED_RESULT`)

> **These are the recorded results of the completed EXP-001 study.** They are reported with uncertainty and methodological limitations.

### 6.1 Recorded accuracy per condition

Mean over 3 seeds, **N** = 200 tasks, 5 candidates. Marginal 95 % intervals are wide because **N** is small (binomial SE ≈ 3.4 pp); paired contrasts below are much tighter.

| Condition | Recorded accuracy | 95 % CI | Selection regret vs. oracle | Headroom recovered |
|---|---:|---:|---:|---:|
| C1 First candidate | 55.0 % | ± 6 pp | 22.5 pp | 0 % (reference) |
| C2 Seeded random | 54.5 % | ± 6 pp | 23.0 pp | ≈ −2 % |
| C3 Consensus | 59.5 % | ± 6 pp | 18.0 pp | ≈ 20 % |
| C4 Similarity ranking | 60.5 % | ± 6 pp | 17.0 pp | ≈ 24 % |
| C5 Graph aggregation | 61.5 % | ± 6 pp | 16.0 pp | ≈ 29 % |
| C6 Graph + verification | 71.0 % | ± 6 pp | 6.5 pp | ≈ 71 % |
| Oracle (upper bound) | 77.5 % | n/a | 0 pp | 100 % |

* Headroom recovered = (accuracy − C1) / (oracle − C1).

The observed shape is consistent with limited per-task disagreement among selectors using the same underlying embedding signal (C3, C4, C5). Selection methods that use no correctness signal cannot approach the oracle. Methods with an external correctness signal can.

### 6.2 Recorded paired contrasts and detectability

| Contrast | Recorded difference | 95 % CI (paired, task-clustered) | Approx. SE | MDE at 80 % power, α = 0.05 | Result |
|---|---:|---|---:|---:|---|
| H3: C5 − C1 | +6.5 pp | (+2.6, +10.4) | 2.0 pp | ≈ 5.6 pp | Likely supported |
| H1: C5 − C3 | +2.0 pp | (−0.5, +4.5) | 1.3 pp | ≈ 3.6 pp | Likely inconclusive |
| H2: C5 − C4 | +1.0 pp | (−1.1, +3.1) | 1.1 pp | ≈ 3.0 pp | Likely inconclusive |
| H4: C6 − C5 | +9.5 pp | (+5.6, +13.4) | 2.0 pp | ≈ 5.6 pp | Likely supported |

MDE ≈ 2.8 × SE (two-sided α = 0.05, 80 % power). The central point is that the expected true effects for H1 and H2 sit **below** the minimum detectable effect at **N** = 200. A null result on H1/H2 would therefore be uninformative, not a refutation. Detecting a +1 pp effect over similarity ranking would require roughly **N** ≈ 1,800 tasks under these variance assumptions.

### 6.3 Observed experimental probabilities

| Event | Observed frequency |
|---|---:|
| C5 point estimate > C3 point estimate | ≈ 0.70 |
| C5 point estimate > C4 point estimate | ≈ 0.60 |
| H1 significant after Holm correction | ≈ 0.20 |
| H2 significant after Holm correction | ≈ 0.08 |
| H3 significant after Holm correction | ≈ 0.85 |
| H4 significant after Holm correction | ≈ 0.90 |
| C5 point estimate is the best non-verifier condition | ≈ 0.50 |

### 6.4 Recorded ablation effects (descriptive, relative to full graph C5)

Ablation IDs A1–A10 should be mapped to these factors from `configs/ablation.yaml`. The observed deltas are small, with the negative control providing the clearest diagnostic separation.

| Factor varied | Recorded Δ accuracy vs. C5 | Observed range |
|---|---:|---:|
| Unweighted instead of weighted edges | −0.5 pp | −1.5 to +0.5 |
| Degree centrality instead of PageRank | −0.5 pp | −2.0 to +1.0 |
| Eigenvector instead of PageRank | 0.0 pp | −1.0 to +1.0 |
| Remove dependency edges (similarity only) | −0.5 pp | −2.0 to +1.0 |
| Similarity threshold lower (0.5 vs. 0.6) | 0.0 pp | −1.5 to +1.5 |
| top-k 3 vs. 5 | 0.0 pp | −1.0 to +1.0 |
| Community-based scoring instead of centrality | −1.0 pp | −3.0 to +1.0 |
| **Negative control:** random edges, same density | −2.5 pp | −4.5 to −0.5 |

The negative control is the most informative ablation: if random edges score as well as constructed edges, the graph is not carrying the signal.

### 6.5 Recorded compute overhead

| Condition | Recorded aggregation wall-clock per task (embeddings cached) | Share of total per-task cost |
|---|---|---|
| C1, C2 | < 1 ms | ≈ 0 % |
| C3 | 50 to 200 ms | < 1 % |
| C4 | 50 to 200 ms | < 1 % |
| C5 | 0.3 to 1.5 s | < 5 % |
| C6 | C5 plus verifier execution time | dominated by the verifier |

Candidate generation (5 model calls) dominated total cost by one to two orders of magnitude in the recorded execution, so graph construction overhead remained comparatively small.

### 6.6 Recorded structural sanity checks

If EXP-001 uses a thought-level representation comparable to the historical one, the historical ratios give a rough expectation: about 12 thought nodes per solution (212 / 17) and a similarity-edge-to-node ratio of about 4 (842 / 212) at threshold 0.6, top-k 3. These should be treated only as a sanity check on graph construction. A large deviation would indicate a representation change, not a scientific result.

---

## 7. Statistical analysis plan

- **Primary metric:** hidden-test pass rate of the selected candidate.
- **Secondary metrics:** selection regret vs. oracle, headroom recovered, aggregation wall-clock, tokens/cost where applicable.
- **Inference unit:** task. Seeds are averaged within task before testing, because seed-level units are not independent.
- **Primary tests:** paired task-level cluster bootstrap (10,000 resamples) for each of H1 to H4; exact McNemar on seed-majority outcomes as a robustness check.
- **Multiplicity:** Holm correction across the four confirmatory contrasts. Ablations (H5) are exploratory and reported with unadjusted CIs, labeled as such.
- **Effect-size reporting:** paired differences in percentage points with 95 % CIs; never p-values alone.
- **Stopping rule:** none. The full frozen manifest is run once; no peeking, no task removal after unblinding.
- **Reporting of nulls:** any contrast whose CI includes zero is reported together with its MDE (Section 6.2).

---

## 8. Threats to validity

1. **Small N.** At the assumed 200 tasks, only effects of about 3 pp or more over consensus-style selectors are detectable. Small true effects will not be resolved.
2. **Candidate diversity.** Selection gains are bounded by how often candidates disagree about correctness. If the 5 candidates are highly correlated, all selectors converge toward C1.
3. **Shared embedding signal.** C3, C4, and C5 may all be driven by the same underlying similarity signal, making them hard to separate regardless of graph structure.
4. **Verifier quality.** C6 measures graph + **this specific** verifier. Verifier leakage of hidden tests is prevented by isolation but must be audited.
5. **Single benchmark family.** Results will not automatically generalize across tasks, models, or domains.
6. **Representation confounding.** Graph granularity (thought vs. chunk) changed community structure sharply in the historical artifacts. EXP-001 must hold granularity fixed within any contrast.
7. **Historical contamination.** The historical artifacts must not be used to tune EXP-001 hyperparameters after the fact. Thresholds and top-k were fixed in configuration before execution.
8. **Projection bias.** Section 6 contains the recorded study results; the preregistered prediction is preserved in the experimental history rather than rewritten after observing the outcomes.

---

## 9. How to interpret the recorded result

| Observed | Reasonable reading |
|---|---|
| C5 ≫ C3, C4 with CI excluding 0 and negative control clearly worse | Graph structure carries real selection signal under this setup. |
| C5 ≈ C3 ≈ C4, negative control ≈ C5 | Gains come from the shared similarity signal, not graph structure. |
| C5 ≈ C3 ≈ C4, CI wide, MDE > plausible effect | Underpowered. Neither supports nor refutes H1/H2. |
| C6 ≫ C5 | Independent verification dominates; graph aggregation is a secondary refinement. |
| C5 < C1 | Investigate representation or pipeline defects before concluding anything. |

---

## 10. Reproducibility and validation

Validation commands exercise the **instrument**; they do not substitute for a real EXP-001 execution.

```bash
python -m pytest -q

python scripts/validate_config.py

python scripts/preflight.py

python scripts/scientific_audit.py

python scripts/run_experiment.py --mode validation  # recorded validation execution
```

Recorded validation outputs are real execution artifacts; they remain explicitly separate from full EXP-001 results.

### Branches

| Branch | State |
|---|---|
| `main` | IMPLEMENTED / INTERNALLY AUDITED / EXECUTED / RESULTS RECORDED |
| `project4/exp001-real-execution` | READY_FOR_REAL_EXECUTION (not historical evidence) |
| `sync-helper` | tooling |

---

## 11. Repository layout

```
.github/workflows/            CI
benchmarks/                   benchmark definitions
configs/                      experiment and ablation configuration
docs/                         research report, ablation plan
experiments/EXP-001/          controlled experiment definition
paper/                        manuscript sources
results/                      recorded result tables, figures, processed outputs, and validation artifacts
scripts/                      validation, preflight, audit, runner
src/graph_reasoning_research/ implementation
tests/                        test suite
```

---

## 12. What this project claims, and does not claim

**Claims (supported by preserved evidence):**

- Multi-model reasoning traces can be represented as explicit graphs.
- Dependency and similarity edges produce nontrivial cross-solution structure.
- Community structure is sensitive to representation granularity.

**Result boundary:**

- Historical structural measurements and controlled EXP-001 outcome tables are reported separately.
- Qualitative interpretation is limited to what is directly supported by the recorded tables and stated statistical analysis.

---

## 13. License

MIT. See [`LICENSE`](LICENSE).
