import numpy as np
from graph_reasoning_research.aggregation.baselines import graph_ranking, random_candidate, similarity_ranking
from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.graph.builders import threshold_graph


def test_random_is_seeded():
    c=MockCandidateGenerator().generate("t","p",5,42)
    assert random_candidate(c,7).selected_candidate_id == random_candidate(c,7).selected_candidate_id


def test_similarity_vs_graph_are_explicit_methods():
    c=MockCandidateGenerator().generate("t","p",4,1)
    x=np.eye(4)
    s=similarity_ranking(c,x)
    g=threshold_graph(c.ids(),x,.5,True)
    r=graph_ranking(c,g,"weighted_degree")
    assert s.method == "similarity_ranking"
    assert r.method.startswith("graph:")
