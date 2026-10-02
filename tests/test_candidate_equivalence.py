import pytest

from graph_reasoning_research.aggregation.baselines import graph_ranking, similarity_ranking
from graph_reasoning_research.generation.base import MockCandidateGenerator, assert_same_candidate_set
from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix


def test_same_candidate_set_hash_used_by_graph_and_similarity():
    candidate_set = MockCandidateGenerator().generate("t", "p", 5, 42)
    representation = HashEmbeddingProvider().encode(candidate_set)
    similarity = cosine_similarity_matrix(representation.embeddings)
    similarity_selection = similarity_ranking(candidate_set, similarity)
    graph_selection = graph_ranking(
        candidate_set,
        threshold_graph(candidate_set.ids(), similarity, 0.2, True),
        "weighted_degree",
    )
    assert_same_candidate_set(candidate_set)
    assert set(similarity_selection.scores) == set(graph_selection.scores)


def test_candidate_set_mismatch_fails_closed():
    first = MockCandidateGenerator().generate("t", "p", 5, 42)
    second = MockCandidateGenerator().generate("t", "p", 5, 43)
    with pytest.raises(ValueError, match="candidate-set equivalence violated"):
        assert_same_candidate_set(first, second)
