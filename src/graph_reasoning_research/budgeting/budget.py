from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass
class BudgetLedger:
    generation_calls: int = 0
    generation_input_tokens: int = 0
    generation_output_tokens: int = 0
    representation_calls: int = 0
    representation_tokens: int = 0
    visible_verification_executions: int = 0
    hidden_verification_executions: int = 0
    graph_construction_ms: float = 0.0
    graph_scoring_ms: float = 0.0
    aggregation_ms: float = 0.0
    candidate_count: int = 0
    max_generation_calls: int = 0
    max_generation_input_tokens: int = 0
    max_generation_output_tokens: int = 0
    max_representation_calls: int = 0
    max_visible_verifications: int = 0
    max_hidden_verifications: int = 0
    max_aggregation_ms: float = 0.0
    max_total_wall_ms: float = 0.0
    started_at: float = 0.0

    def __post_init__(self):
        if not self.started_at:
            self.started_at = time.perf_counter()

    @property
    def verification_executions(self) -> int:
        return self.visible_verification_executions + self.hidden_verification_executions

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.started_at) * 1000.0

    def ensure_wall_budget(self):
        if self.max_total_wall_ms and self.elapsed_ms >= self.max_total_wall_ms:
            raise RuntimeError("budget_ineligibility: total wall-clock budget exceeded before next operation")

    def reserve_generation(self, input_tokens=0, output_tokens=0, calls=1):
        self.ensure_wall_budget()
        if self.generation_calls + calls > self.max_generation_calls:
            raise RuntimeError("budget_ineligibility: generation call budget exceeded")
        if self.generation_input_tokens + input_tokens > self.max_generation_input_tokens:
            raise RuntimeError("budget_ineligibility: generation input-token budget exceeded")
        if self.generation_output_tokens + output_tokens > self.max_generation_output_tokens:
            raise RuntimeError("budget_ineligibility: generation output-token budget exceeded")
        self.generation_calls += calls
        self.generation_input_tokens += input_tokens
        self.generation_output_tokens += output_tokens

    def reserve_representation(self, tokens=0, calls=1):
        self.ensure_wall_budget()
        if self.representation_calls + calls > self.max_representation_calls:
            raise RuntimeError("budget_ineligibility: representation call budget exceeded")
        self.representation_calls += calls
        self.representation_tokens += tokens

    def reserve_visible_verification(self, calls=1):
        self.ensure_wall_budget()
        if self.visible_verification_executions + calls > self.max_visible_verifications:
            raise RuntimeError("budget_ineligibility: visible verification budget exceeded")
        self.visible_verification_executions += calls

    def reserve_hidden_verification(self, calls=1):
        self.ensure_wall_budget()
        if self.hidden_verification_executions + calls > self.max_hidden_verifications:
            raise RuntimeError("budget_ineligibility: hidden verification budget exceeded")
        self.hidden_verification_executions += calls

    def record_candidates(self, count):
        self.candidate_count = count

    def record_graph(self, construction_ms, scoring_ms):
        self.ensure_wall_budget()
        self.graph_construction_ms += construction_ms
        self.graph_scoring_ms += scoring_ms
        self.aggregation_ms += construction_ms + scoring_ms
        if self.max_aggregation_ms and self.aggregation_ms > self.max_aggregation_ms:
            raise RuntimeError("budget_ineligibility: aggregation wall-clock budget exceeded")
