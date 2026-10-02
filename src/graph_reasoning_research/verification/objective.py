from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from graph_reasoning_research.types import Candidate, CandidateEvaluation
class ObjectiveVerifier(Protocol):
    def evaluate(self,candidate:Candidate,*,hidden:bool=False)->CandidateEvaluation: ...
@dataclass
class MockObjectiveVerifier:
    def evaluate(self,candidate:Candidate,*,hidden:bool=False)->CandidateEvaluation:
        value=candidate.metadata.get('mock_objective',0.0); result='PASS' if float(value)>0.5 else 'FAIL'; return CandidateEvaluation(candidate.candidate_id,result,result,result if hidden else None)
