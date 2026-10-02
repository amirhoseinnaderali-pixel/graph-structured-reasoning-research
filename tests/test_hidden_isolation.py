import copy

from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.graph.scoring import weighted_degree
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.types import Candidate, CandidateSet


def _decision_fingerprint(candidate_set: CandidateSet):
    representation = HashEmbeddingProvider().encode(candidate_set)
    similarity = cosine_similarity_matrix(representation.embeddings)
    graph = threshold_graph(candidate_set.ids(), similarity, 0.25, True)
    return (
        candidate_set.ids(),
        candidate_set.candidate_set_hash,
        representation.representation_hash,
        tuple(graph.edges),
        weighted_degree(graph),
    )


def test_hidden_results_do_not_enter_graph_inputs():
    original = MockCandidateGenerator().generate("t", "p", 5, 42)
    baseline = _decision_fingerprint(original)
    mutated = tuple(
        Candidate(
            c.candidate_id,
            c.task_id,
            c.text,
            c.answer,
            c.generator_model_id,
            c.seed,
            c.generation_config_hash,
            c.output_hash,
            {**copy.deepcopy(c.metadata), "hidden_result": "different"},
        )
        for c in original.candidates
    )
    mutated_set = CandidateSet(original.task_id, mutated, original.candidate_set_hash)
    assert _decision_fingerprint(mutated_set) == baseline
