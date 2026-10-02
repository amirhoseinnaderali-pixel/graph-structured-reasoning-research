# Evaluation

For programming tasks, only visible tests may be used for candidate selection when the experiment permits objective verification. Hidden tests are evaluation-only. They cannot enter candidate representations, embeddings, similarities, graph construction, graph scoring, ranking, or selection.

The verifier interface separates `evaluate_visible()` and `evaluate_hidden()`. Infrastructure failures are distinct from wrong answers, malformed output, and timeouts.

Primary outcome: objective correctness of the selected candidate. Secondary outcomes include candidate-selection agreement, graph-vs-similarity disagreement, graph density, aggregation latency, verification latency, generation/representation cost, and failure categories.
