# Evaluation

The selected candidate is evaluated objectively using the programming task's frozen test suites.

## Information boundary

Candidate generation receives the problem statement only. Representation receives candidate text only. Similarity, consensus, graph construction, graph scoring, and selection do not receive hidden tests.

C5 is the only condition that uses visible verification during selection. It first forms a graph-derived shortlist and then verifies the shortlisted candidates using visible assertions only.

After a strategy has selected exactly one candidate, the independent hidden verifier evaluates that selected candidate. Hidden evaluation is never fed back into selection.

## Primary outcome

The primary empirical outcome is hidden objective correctness of the selected candidate.

Secondary accounting includes task-level hidden solved rate, aggregation latency, candidate count, generation calls/tokens, representation calls/latency, visible verification executions, graph construction/scoring time, graph density, and failure classes.

Repeated seeds are analyzed at task level, with paired differences against the similarity baseline and an uncertainty interval. No significance claim is produced without actual experimental data.

Infrastructure failures and budget ineligibility are not converted into wrong answers.
