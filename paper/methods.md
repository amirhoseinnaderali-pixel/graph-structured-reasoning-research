# Methods

## Controlled comparison

EXP-001 fixes the candidate set and varies only aggregation/selection. Candidate generation is materialized once per task-seed pair and identified by `candidate_set_hash`. Graph and similarity conditions consume the same candidate IDs, outputs, representation model/configuration, and similarity matrix.

## Representation

Representation configuration is explicit and hashed. Graph construction uses the representation artifact and cannot access hidden evaluation outputs.

## Graphs

Threshold and k-NN graphs are supported, with weighted and unweighted edges. Scoring includes weighted degree, degree centrality, PageRank, and local-neighborhood agreement. Graph parameters and configuration hashes are recorded with every run.

## Objective evaluation

For programming tasks, visible tests are selection-visible information. Hidden tests are evaluation-only and are never inputs to representation, similarity, graph construction, graph scoring, ranking, or candidate selection.

## Compute

Generation calls/tokens, representation calls/tokens/latency, similarity latency, graph construction/scoring latency, selection latency, visible verification, and hidden evaluation are separately recorded.

## Current experimental status

The controlled EXP-001 study has been executed and its results are recorded in the repository. Runtime credentials and environment details for future reruns remain separately documented.
