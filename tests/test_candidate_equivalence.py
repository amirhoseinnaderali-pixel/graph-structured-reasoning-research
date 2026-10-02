from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.aggregation.baselines import similarity_ranking, graph_ranking
from graph_reasoning_research.graph.builders import threshold_graph

def test_same_candidate_set_hash_used_by_graph_and_similarity():
    c=MockCandidateGenerator().generate('t','p',5,42); rep=HashEmbeddingProvider().encode(c); sim=cosine_similarity_matrix(rep.embeddings); sg=similarity_ranking(c,sim); gg=graph_ranking(c,threshold_graph(c.ids(),sim,.2,True),'weighted_degree')
    assert c.candidate_set_hash==c.candidate_set_hash; assert set(sg.scores)==set(gg.scores)
