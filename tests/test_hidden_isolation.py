from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.types import Candidate
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.graph.builders import threshold_graph
from graph_reasoning_research.graph.scoring import weighted_degree

def test_hidden_results_do_not_enter_graph_inputs():
    c=MockCandidateGenerator().generate('t','p',5,42); baseline=HashEmbeddingProvider().encode(c); sim=cosine_similarity_matrix(baseline.embeddings); g=threshold_graph(c.ids(),sim,.25,True); before=(g.edges,weighted_degree(g))
    mutated=tuple(Candidate(x.candidate_id,x.task_id,x.text,x.answer,x.generator_id,{'hidden_result':'different'}) for x in c.candidates); mutated_set=c.__class__(c.task_id,mutated,c.candidate_set_hash); assert mutated_set.ids()==c.ids(); baseline_rep=HashEmbeddingProvider().encode(mutated_set); sim2=cosine_similarity_matrix(baseline_rep.embeddings); g2=threshold_graph(mutated_set.ids(),sim2,.25,True); after=(g2.edges,weighted_degree(g2)); assert before==after
