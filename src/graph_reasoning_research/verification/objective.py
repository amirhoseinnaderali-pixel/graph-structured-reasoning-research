from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from graph_reasoning_research.types import Candidate, CandidateEvaluation


class ObjectiveVerifier(Protocol):
    def evaluate_visible(self, candidate: Candidate) -> CandidateEvaluation: ...

    def evaluate_hidden(self, candidate: Candidate) -> CandidateEvaluation: ...


@dataclass
class MockObjectiveVerifier:
    def evaluate_visible(self, candidate: Candidate) -> CandidateEvaluation:
        value = float(candidate.metadata.get("mock_objective", 0.0))
        result = "PASS" if value > 0.5 else "FAIL"
        return CandidateEvaluation(candidate.candidate_id, result, visible_result=result)

    def evaluate_hidden(self, candidate: Candidate) -> CandidateEvaluation:
        value = float(candidate.metadata.get("mock_objective", 0.0))
        result = "PASS" if value > 0.5 else "FAIL"
        return CandidateEvaluation(candidate.candidate_id, result, hidden_result=result)
