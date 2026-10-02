import numpy as np

from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.graph.scoring import degree_centrality, pagerank, weighted_degree
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix


def test_similarity_is_symmetric_and_normalized():
    x = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    similarity = cosine_similarity_matrix(x)
    assert np.allclose(similarity, similarity.T)
    assert np.allclose(np.diag(similarity), 1.0)


def test_graph_scores_cover_all_nodes():
    ids = ("a", "b", "c")
    similarity = np.array([[1, 0.9, 0.2], [0.9, 1, 0.8], [0.2, 0.8, 1]])
    graph = threshold_graph(ids, similarity, 0.5, True)
    assert set(weighted_degree(graph)) == set(ids)
    assert set(degree_centrality(graph)) == set(ids)
    assert set(pagerank(graph)) == set(ids)


def test_unweighted_graph_and_pagerank_are_deterministic():
    ids = ("a", "b", "c")
    similarity = np.array([[1, 0.9, 0.2], [0.9, 1, 0.8], [0.2, 0.8, 1]])
    graph = threshold_graph(ids, similarity, 0.5, False)
    assert all(weight == 1.0 for _, _, weight in graph.edges)
    assert pagerank(graph) == pagerank(graph)
