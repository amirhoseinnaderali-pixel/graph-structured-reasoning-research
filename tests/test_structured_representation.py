from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.representations.structured import StructuredReasoningProvider
from graph_reasoning_research.types import Candidate

def test_structured_reasoning_steps_are_supported():
    c=MockCandidateGenerator().generate('t','p',2,42); cands=tuple(Candidate(x.candidate_id,x.task_id,x.text,x.answer,x.generator_id,{'reasoning_steps':['step one','step two']}) for x in c.candidates); cs=c.__class__(c.task_id,cands,c.candidate_set_hash); rep=StructuredReasoningProvider().encode(cs); assert rep.method=='structured_reasoning_hash_embedding'; assert rep.embeddings.shape[0]==2
