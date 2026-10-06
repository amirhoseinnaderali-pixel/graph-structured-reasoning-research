import numpy as np
from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.graph.scoring import degree_centrality, pagerank, weighted_degree
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix


def test_similarity_is_symmetric_and_normalized():
    x=np.array([[1.,0.],[0.,1.],[1.,1.]])
    s=cosine_similarity_matrix(x)
    assert np.allclose(s, s.T)
    assert np.allclose(np.diag(s), 1.)


def test_graph_scores_cover_all_nodes():
    ids=("a","b","c")
    s=np.array([[1,.9,.2],[.9,1,.8],[.2,.8,1.]])
    g=threshold_graph(ids,s,.5,True)
    assert set(weighted_degree(g))==set(ids)
    assert set(degree_centrality(g))==set(ids)
    assert set(pagerank(g))==set(ids)


def test_unweighted_graph_and_pagerank_are_deterministic():
    from graph_reasoning_research.graph.builders import threshold_graph
    ids=("a","b","c"); sim=np.array([[1,.9,.2],[.9,1,.8],[.2,.8,1.]])
    g=threshold_graph(ids,sim,.5,False)
    assert all(weight == 1.0 for _,_,weight in g.edges)
    from graph_reasoning_research.graph.scoring import pagerank
    assert pagerank(g) == pagerank(g)
