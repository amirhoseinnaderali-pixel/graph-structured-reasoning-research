from __future__ import annotations
from dataclasses import dataclass
@dataclass
class BudgetLedger:
    candidate_calls: int = 0
    generation_tokens: int = 0
    embedding_calls: int = 0
    verification_executions: int = 0
    max_candidate_calls: int = 0
    max_generation_tokens: int = 0
    max_embedding_calls: int = 0
    max_verification_executions: int = 0
    def reserve_generation(self, tokens: int) -> None:
        if self.candidate_calls + 1 > self.max_candidate_calls: raise RuntimeError("candidate call budget exceeded")
        if self.generation_tokens + tokens > self.max_generation_tokens: raise RuntimeError("generation token budget exceeded")
        self.candidate_calls += 1; self.generation_tokens += tokens
    def reserve_embedding(self) -> None:
        if self.embedding_calls + 1 > self.max_embedding_calls: raise RuntimeError("embedding budget exceeded")
        self.embedding_calls += 1
    def reserve_verification(self) -> None:
        if self.verification_executions + 1 > self.max_verification_executions: raise RuntimeError("verification budget exceeded")
        self.verification_executions += 1
