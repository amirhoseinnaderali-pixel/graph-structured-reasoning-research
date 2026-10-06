import numpy as np
import pytest

from graph_reasoning_research.generation.base import MockCandidateGenerator, assert_same_candidate_set
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.aggregation.baselines import similarity_ranking
from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.aggregation.baselines import graph_ranking


def test_same_candidate_set_hash_used_by_graph_and_similarity():
    c=MockCandidateGenerator().generate("t","p",5,42)
    rep=HashEmbeddingProvider().encode(c)
    sim=cosine_similarity_matrix(rep.embeddings)
    sg=similarity_ranking(c,sim)
    gg=graph_ranking(c,threshold_graph(c.ids(),sim,.2,True),"weighted_degree")
    assert_same_candidate_set(c)
    assert set(sg.scores) == set(gg.scores)


def test_candidate_set_mismatch_fails_closed():
    first = MockCandidateGenerator().generate("t", "p", 5, 42)
    second = MockCandidateGenerator().generate("t", "p", 5, 43)
    with pytest.raises(ValueError, match="candidate-set equivalence violated"):
        assert_same_candidate_set(first, second)
