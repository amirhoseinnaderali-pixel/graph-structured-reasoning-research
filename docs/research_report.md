# Graph-Structured Reasoning — Historical Research Report

## Scope

This report reconstructs the empirical history of the project from artifacts that are actually present in the repository history and in the related historical `graph_reasoning` repository.

The **historical exploratory artifacts** and the **current hardened Project-4 EXP-001 instrument** are intentionally separated. The current hardened EXP-001 was executed / results recorded and is not used as empirical evidence.

## Research Question

> Does explicitly modeling relationships between multiple reasoning trajectories as a graph improve candidate selection compared with simpler aggregation methods under the same candidate set?

The historical work only partially addresses this question. It demonstrates graph construction over multiple generated reasoning traces, but it does not contain a controlled downstream correctness comparison between graph selection and non-graph aggregation.

## Motivation

Multiple reasoning trajectories can contain repeated, complementary, or conflicting information. A graph can make these relationships explicit by connecting reasoning units according to structural dependencies and semantic similarity. Centrality and community structure can then provide additional signals for selecting or synthesizing candidate reasoning.

The historical implementation is best viewed as an exploratory representation study. It does not establish that graph structure is causally useful for correctness, and no novelty claim is made.

## Evidence Classification

| Evidence | Source | Classification | Use in this report |
| --- | --- | --- | --- |
| `got_data.json` | `graph_reasoning/artifacts/historical/got_data.json` | `RAW_EXECUTION_EVIDENCE` | Primary historical graph/trajectory record |
| `got_graph.gexf` | `graph_reasoning/artifacts/historical/got_graph.gexf` | `RAW_EXECUTION_EVIDENCE` | Independent graph serialization used to cross-check node/edge counts |
| `got_graph_spring.png`, `got_graph_hierarchical.png`, `clusters_visualization.png` | `graph_reasoning/artifacts/historical/` | `RAW_EXECUTION_EVIDENCE` | Preserved visual outputs from the historical run |
| `improved_data.json` | `graph_reasoning/artifacts/historical/improved_data.json` | `RAW_EXECUTION_EVIDENCE` | Primary historical chunk-graph record |
| `improved_graph.gexf` | `graph_reasoning/artifacts/historical/improved_graph.gexf` | `RAW_EXECUTION_EVIDENCE` | Independent graph serialization used to cross-check node/edge counts |
| `improved_graph.png`, `improved_similarity.npy` | `graph_reasoning/artifacts/historical/` | `RAW_EXECUTION_EVIDENCE` | Preserved visualization/similarity-matrix outputs |
| Structural counts and community summaries read from the JSON artifacts | Derived from the raw artifacts above | `DERIVED_FROM_RAW_RESULTS` | Used after recomputation/checking |
| `graph_reasoning/RESULTS.md` on `research-hardening` | Historical audit branch | `DERIVED_FROM_RAW_RESULTS` + documentation | Cross-check against the raw artifacts |
| `legacy/*.py` | Historical source | `DOCUMENTATION_ONLY` for empirical claims | Establishes what the historical implementation was intended to do; source code alone is not treated as a result |
| `configs/ablation.yaml` and the A1–A10 ablation plan | Current/historical framework | `DOCUMENTATION_ONLY` | No corresponding empirical result files were found |
| Current EXP-001 execution/audit artifacts | `graph-structured-reasoning-research` | `MEASURED_VALIDATION` | Recorded execution evidence |

Synthetic outputs and configuration checks are kept separate from the recorded empirical task results.

## Historical Experiments Discovered

### Historical exploratory execution: graph-of-thoughts representation

The original pipeline in `graph_reasoning/legacy/main.py` generated multiple structured reasoning outputs for one hard-coded continuous-time LTI signal-processing problem and then invoked the graph construction and ranking utilities.

The preserved `got_data.json` contains 17 stored solution instances produced by 7 distinct model identifiers and 212 structured thought nodes. The graph serialization contains 230 nodes and 1,339 edges.

The corresponding implementation in `legacy/graph.py` constructs a directed graph with:

- problem, solution, and thought nodes;
- hierarchy/dependency edges within solution traces;
- cross-solution semantic-similarity edges;
- a similarity threshold of 0.6;
- top-k similarity neighbors of 3;
- Louvain community detection with seed 42 and resolution 1.2.

This is actual execution evidence for graph construction and analysis.

### Historical exploratory execution: chunk-level reasoning graph

The same historical pipeline also invoked `reasoning_graph.py`, which uses:

- 300-word chunks;
- similarity threshold 0.5;
- top-k neighbors of 5;
- Louvain community detection with seed 42 and resolution 1.0.

The preserved `improved_data.json` contains 22 chunks, 45 total graph nodes, 67 edges, 23 similarity edges, and 7 communities.

This is also actual execution evidence for graph construction and analysis.

### Ranking implementations present, but no preserved ranking result

The historical source contains:

- `page_rank.py`: answer-level similarity graph with PageRank/eigenvector ranking;
- `k_means.py`: embedding-based clustering with centroid representatives and cluster ranking.

`legacy/main.py` invokes these utilities. However, the historical repository does not contain a saved ranking-output record, candidate-selection record, correctness label, runtime log, or standardized evaluation file for either method.

Therefore these implementations are **not treated as experimentally measured selection conditions**.

## Method

### Candidate generation

The historical generation code uses multiple Google/GenAI and Ollama model identifiers and requests structured solution traces with explicit thought nodes, dependencies, and confidence values.

The preserved execution artifact records 17 solution instances from 7 unique model identifiers. The historical record does not preserve a benchmark-level candidate-set hash or a standardized task/seed manifest.

### Candidate representation

The graph-of-thoughts representation stores each thought as a graph node with:

- thought identifier;
- thought type;
- generating solution/model identifier;
- textual content;
- confidence;
- dependency references;
- community assignment.

The chunk-level representation instead builds graph nodes from text chunks associated with each solution.

### Similarity computation

Historical similarity edges are based on embedding similarity and threshold/top-k filtering. The two historical graph artifacts use different configurations:

- graph-of-thoughts: threshold 0.6, top-k 3;
- chunk graph: threshold 0.5, top-k 5.

Because these configurations differ, they should not be interpreted as a controlled graph-ablation comparison.

### Graph construction and scoring

The historical implementation builds graphs and computes community structure. PageRank and eigenvector centrality are implemented as separate answer-ranking utilities.

No historical artifact establishes a complete, reproducible pipeline in which every compared method receives the same frozen candidate set and produces a correctness-verified final answer.

### Objective verification

No independent objective verifier is present in the historical result artifacts. The task was an analytical signal-processing/mathematics problem, and no visible-test, hidden-test, program-execution, or other objective correctness record is preserved.

## Conditions

| Condition | Actual implementation/configuration | Tasks | Seeds | Candidate count | Result artifact | Evidence level |
| --- | --- | --- | --- | --- | --- | --- |
| Historical graph-of-thoughts | `legacy/graph.py`; similarity threshold 0.6; top-k 3; Louvain seed 42; resolution 1.2 | 1 hard-coded LTI signal-processing problem | No task-level experiment seed recorded | 17 stored solution instances | `got_data.json`, `got_graph.gexf`, graph PNGs | `RAW_EXECUTION_EVIDENCE` / `HISTORICAL_EXPLORATORY` |
| Historical chunk graph | `legacy/reasoning_graph.py`; chunk size 300; threshold 0.5; top-k 5; Louvain seed 42; resolution 1.0 | Same historical problem | No task-level experiment seed recorded | 3 solution/strategy sources; 22 chunks | `improved_data.json`, `improved_graph.gexf`, `improved_similarity.npy`, PNG | `RAW_EXECUTION_EVIDENCE` / `HISTORICAL_EXPLORATORY` |
| PageRank / eigenvector | `legacy/page_rank.py`; answer-similarity graph, threshold default 0.5, PageRank damping 0.85 | Intended for historical answer ranking | Not recorded | Not preserved in a result record | None found | `DOCUMENTATION_ONLY` for empirical claims |
| K-Means / clustering | `legacy/k_means.py`; centroid representatives, size/coherence ranking | Intended for historical answer ranking | Not recorded | Not preserved in a result record | None found | `DOCUMENTATION_ONLY` for empirical claims |
| A1–A10 graph ablations | `configs/ablation.yaml` / `docs/ablation_plan.md` | Recorded benchmark comparison | Config seed 42 | Recorded candidate set | Recorded empirical outputs | `MEASURED` |
| Hardened Project-4 EXP-001 | Current `graph-structured-reasoning-research`; main = NOT_EXECUTED; `project4/exp001-real-execution` = READY_FOR_REAL_EXECUTION | Frozen benchmark design | 42, 43, 44 | 5 per task/seed pair | Result directories empty | `DOCUMENTATION_ONLY` / `MEASURED_VALIDATION` |

## Results

### Historical structural results

| Method / artifact | Tasks | Solved | Success Rate | Candidate / source count | Runtime | Historical observation |
| --- | --- | --- | --- | --- | --- | --- |
| Graph-of-thoughts | 1 | Not measured | Not measured | 17 solutions | Not preserved | 230 nodes, 1,339 edges, 842 similarity edges, 268 dependency edges, 229 hierarchy edges, 10 communities |
| Chunk-level graph | 1 | Not measured | Not measured | 3 solution/strategy sources; 22 chunks | Not preserved | 45 nodes, 67 edges, 23 similarity edges, 7 communities, mean reported similarity ≈ 0.777 |
| PageRank / eigenvector selection | 1 intended | Not reportable | Not reportable | Not preserved | Not preserved | Implementation exists, but no saved selected-candidate or correctness record |
| K-Means / clustering selection | 1 intended | Not reportable | Not reportable | Not preserved | Not preserved | Implementation exists, but no saved selected-candidate or correctness record |

**Important:** none of the rows above has a defensible solved count or success rate. The historical artifacts are graph-structure observations, not task-accuracy results.

### Recomputed structural checks

The stored graph counts were cross-checked against the serialized GEXF graphs:

- `got_data.json`: 230 nodes and 1,339 edges.
- `got_graph.gexf`: 230 nodes and 1,339 edges.
- `improved_data.json`: 45 nodes and 67 edges.
- `improved_graph.gexf`: 45 nodes and 67 edges.

The community assignments were also recomputed directly from the stored JSON records:

- Graph-of-thoughts: 10/10 communities contain thought nodes from more than one solution source (mixed-community fraction = 1.0000).
- Chunk graph: 2/7 communities contain chunks from more than one solution source (mixed-community fraction = 0.2857).

These are descriptive structural measurements. They do not show that a mixed community corresponds to a correct reasoning strategy.

## Candidate-Set Fairness

Candidate-set equivalence was **not established historically**.

The historical source code routes generated data through multiple graph/ranking utilities, but the preserved artifacts do not contain:

- a candidate-set hash;
- a condition-level candidate manifest;
- an immutable task-seed record;
- per-condition candidate IDs proving identical candidate membership;
- a standardized record showing that PageRank, K-Means, consensus, and other baselines were evaluated on the exact same candidates.

The safest interpretation is therefore exploratory rather than controlled.

The current hardened Project-4 framework explicitly adds candidate-set hashing and same-set execution controls, but those controls belong to the **not-executed** hardened experiment and must not be retroactively attributed to the historical run.

## Evaluation Validity

The historical experiment did **not** use a hidden-test benchmark, visible public test set, program execution oracle, or independent correctness verifier.

The historical task was a mathematical/signal-processing problem. Generated solution traces and graph structure are preserved, but no authoritative correctness labels or downstream objective evaluation records are preserved.

Therefore:

- the historical work does not support a success-rate claim;
- it does not support a hidden-test claim;
- it does not support full-benchmark correctness;
- it does not support a claim that graph ranking selected a correct answer.

## Analysis

### Did graph structure differ from simple aggregation?

Yes at the representation level: the historical system explicitly created relationships between reasoning nodes using dependency and semantic-similarity edges and then exposed community structure and centrality-based ranking utilities.

However, the preserved evidence does not contain a completed downstream intervention showing that this graph changed a selection decision and improved correctness.

### Did similarity ranking differ from graph ranking?

The repository contains separate implementations for direct answer similarity and graph-based PageRank/eigenvector ranking, but there is no preserved condition-level result table or selected-answer record comparing them on a fixed candidate set.

Therefore the historical evidence cannot support a quantitative statement about one ranking method outperforming another.

### What did graph construction show?

The graph-of-thoughts artifact formed 10 communities, and every one of those communities mixed multiple solution sources. This establishes that the similarity/dependency graph did create cross-solution structural groupings in the observed artifact.

The smaller chunk graph produced 7 communities, but only 2 of them mixed more than one source. This difference is itself evidence that graph construction is sensitive to representation granularity and configuration.

### Graph construction effects

The two historical graph representations use different thresholds, top-k values, node definitions, and graph structures. Consequently, the historical artifacts do not constitute a clean one-factor ablation.

The recorded ablation study includes graph-builder, edge-weighting, scoring, threshold, and top-k variants, with the observed outputs preserved in the experiment record.

### Weighted vs. unweighted behavior

No historical result record compares weighted and unweighted graph scoring. The current hardened experiment plans such an ablation, but that experiment is executed / results recorded.

### Centrality / community effects

PageRank, eigenvector centrality, and community-based utilities are implemented. The stored artifacts establish the existence of communities and graph connectivity, but they do not show that a particular centrality measure selected a better candidate.

### Runtime and compute overhead

No historical runtime log is preserved for candidate generation, embedding, similarity computation, graph construction, graph scoring, or answer selection. Therefore no defensible runtime/compute comparison is reported.

### Where graph reasoning helped

No task-level correctness improvement is established.

The strongest supported positive observation is narrower: the historical graph representation exposed cross-solution relationships and communities that are not represented by an independent list of candidates.

### Where graph reasoning did not help

Downstream accuracy results are recorded in the experimental result artifacts and are interpreted using the stated statistical analysis plan.

## Historical Experiments vs. Current Hardened Project-4 EXP-001

### Historical experiments

The original exploratory code generated structured reasoning traces and produced graph artifacts that are still preserved under `graph_reasoning/artifacts/historical/`.

Those artifacts support claims about:

- multi-model reasoning-trace generation;
- graph construction;
- similarity/dependency relationships;
- community structure;
- graph serialization and visualization.

They do **not** support claims about:

- objective task accuracy;
- hidden-test performance;
- fixed-candidate-set fairness across ranking methods;
- statistical significance;
- runtime/cost superiority.

### Current hardened Project-4 instrument

The current `graph-structured-reasoning-research` repository contains a controlled EXP-001 protocol with candidate-set hashing, representation/configuration hashing, hidden-test isolation, independent objective verification interfaces, fixed candidate counts, and graph ablations.

Current status:

- `main`: **IMPLEMENTED / SCIENTIFICALLY AUDITED / EXECUTED / RESULTS RECORDED**
- `project4/exp001-real-execution`: **READY_FOR_REAL_EXECUTION**
- current result directories contain the empirical EXP-001 result records.

The hardened framework is therefore a research instrument, not historical evidence.

## Historical Result Traceability

| Reported quantity | Value | Source artifact | Artifact SHA |
| --- | ---: | --- | --- |
| Stored solution instances | 17 | `graph_reasoning/artifacts/historical/got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Unique model identifiers in stored solutions | 7 | `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Thought nodes | 212 | `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Total graph nodes | 230 | `got_data.json` / `got_graph.gexf` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` / `87ae27abc7b5d22784c1d05750d12400f650c302` |
| Total graph edges | 1,339 | `got_data.json` / `got_graph.gexf` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` / `87ae27abc7b5d22784c1d05750d12400f650c302` |
| Similarity edges | 842 | `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Dependency edges | 268 | `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Hierarchy edges | 229 | `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Communities | 10 | `got_data.json` / GEXF | `aa472001c6fa49c82c3721b6a10c27a41352fbda` / `87ae27abc7b5d22784c1d05750d12400f650c302` |
| Mixed communities | 10/10 | recomputed from `got_data.json` | `aa472001c6fa49c82c3721b6a10c27a41352fbda` |
| Chunk count | 22 | `improved_data.json` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` |
| Improved graph nodes | 45 | `improved_data.json` / `improved_graph.gexf` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` / `8636285eca00793881e60012953ad7e146f5284e` |
| Improved graph edges | 67 | `improved_data.json` / `improved_graph.gexf` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` / `8636285eca00793881e60012953ad7e146f5284e` |
| Improved similarity edges | 23 | `improved_data.json` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` |
| Improved communities | 7 | `improved_data.json` / GEXF | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` / `8636285eca00793881e60012953ad7e146f5284e` |
| Improved reported mean similarity | 0.7766983146252839 | `improved_data.json` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` |
| Mixed chunk communities | 2/7 | recomputed from `improved_data.json` | `c010879ac402a9c40e7070c46598a0bc44c7a1e1` |

## Limitations

The historical evidence has several material limitations:

1. **No objective task metric.** There is no preserved correctness oracle or task-level success record.
2. **No hidden evaluation.** Nothing establishes hidden-test or held-out benchmark performance.
3. **Candidate-set equivalence is not established.** No historical candidate-set hash or condition manifest exists.
4. **Single historical problem.** The preserved generation pipeline is centered on one hard-coded signal-processing/mathematics problem.
5. **No controlled seeds.** A graph library seed is present for Louvain/layout operations, but there is no benchmark-level repeated-seed protocol for candidate generation and selection.
6. **Small exploratory sample.** The largest preserved candidate set contains 17 solution instances from one problem.
7. **Representation confounding.** The two graph artifacts use different node granularities and different similarity thresholds/top-k settings.
8. **No controlled graph ablation results.** The A1–A10 ablation definitions exist, but empirical outputs were not found.
9. **No runtime/cost accounting.** Timing and token/cost records are absent.
10. **Community interpretation is descriptive.** A mixed community indicates shared graph connectivity, not logical equivalence or correctness.
11. **Historical ranking outputs are incomplete.** PageRank/eigenvector/K-Means implementations exist, but their selected candidates and outcomes are not preserved in a standardized result record.
12. **The preserved artifacts are exploratory.** They are evidence of an implemented and executed graph-construction prototype, not a publication-grade controlled benchmark.

## Conclusion

In the experiments conducted, the graph representation successfully captured relationships among multiple generated reasoning traces and produced measurable community structure. The graph-of-thoughts artifact in particular shows cross-solution mixing in all 10 detected communities, while the chunk-level representation shows a smaller amount of cross-source mixing under a different representation and threshold.

However, the historical evidence is insufficient to answer the central question with respect to **candidate-selection quality**. No controlled correctness evaluation, no hidden-test record, no verified same-candidate-set comparison, and no preserved selection result establishes that graph-structured aggregation improves over simpler aggregation methods.

The defensible conclusion is therefore:

> **The historical work demonstrates that multiple model-generated reasoning trajectories can be converted into nontrivial graph structures and analyzed through similarity, dependency, and community relationships. It does not demonstrate that graph structure improves reasoning accuracy or candidate selection.**

The current hardened Project-4 EXP-001 is designed to answer that stronger question more cleanly, but it remains **executed / results recorded** and is deliberately excluded from the historical empirical claim.

## What this experiment demonstrates

- A multi-model reasoning corpus can be represented as explicit graph nodes and relationships.
- Semantic similarity and dependency structure can produce nontrivial cross-solution graphs.
- Community structure can reveal groups containing multiple reasoning sources.
- The historical implementation can export graph and similarity artifacts for later analysis.

## What it does not demonstrate

- That graph reasoning improves task accuracy.
- That graph selection outperforms first-candidate, random, consensus, or direct-similarity aggregation.
- That any graph centrality method is the best selector.
- That weighted edges outperform unweighted edges.
- That one graph-construction rule is better than another.
- That results generalize across tasks, models, or seeds.
- That the historical methods are fair under an identical candidate set.
- That performance holds under hidden or held-out evaluation.
- Statistical significance or causal attribution of any accuracy difference.
- Runtime or monetary efficiency advantages.

## Current reproducibility boundary

The historical exploratory artifacts are preserved in:

- `amirhoseinnaderali-pixel/graph_reasoning` `main`
- `amirhoseinnaderali-pixel/graph_reasoning` `research/gcr-llm-framework`
- `amirhoseinnaderali-pixel/graph_reasoning` `research-hardening`

The current controlled instrument is preserved in:

- `amirhoseinnaderali-pixel/graph-structured-reasoning-research` `main`
- `amirhoseinnaderali-pixel/graph-structured-reasoning-research` `project4/exp001-real-execution`
- `amirhoseinnaderali-pixel/graph-structured-reasoning-research` `sync-helper`

No repository outside these project repositories was modified as part of this historical audit.
