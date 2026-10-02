from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from graph_reasoning_research.types import Candidate, CandidateSet
class CandidateGenerator:
    def generate(self,task_id:str,problem:str,n:int,seed:int)->CandidateSet: raise NotImplementedError
def candidate_set_hash(candidates:list[Candidate])->str:
    payload=[{'candidate_id':c.candidate_id,'text':c.text,'answer':c.answer} for c in candidates]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass
class MockCandidateGenerator(CandidateGenerator):
    def generate(self,task_id:str,problem:str,n:int,seed:int)->CandidateSet:
        candidates=[]
        for i in range(n):
            variant=(i+seed)%max(n,1); text=f'Mock solution {i} for {problem}. Reasoning variant {variant}.'; answer=str(variant%2); candidates.append(Candidate(f'{task_id}-c{i}',task_id,text,answer))
        return CandidateSet(task_id,tuple(candidates),candidate_set_hash(candidates))
