from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetLedger:
    generation_calls: int = 0
    generation_input_tokens: int = 0
    generation_output_tokens: int = 0
    representation_calls: int = 0
    representation_tokens: int = 0
    verification_executions: int = 0
    max_generation_calls: int = 0
    max_generation_input_tokens: int = 0
    max_generation_output_tokens: int = 0
    max_representation_calls: int = 0
    max_verification_executions: int = 0

    def reserve_generation(self, input_tokens: int = 0, output_tokens: int = 0, calls: int = 1) -> None:
        if calls < 1:
            raise ValueError("calls must be positive")
        if self.generation_calls + calls > self.max_generation_calls:
            raise RuntimeError("generation call budget exceeded")
        if self.generation_input_tokens + input_tokens > self.max_generation_input_tokens:
            raise RuntimeError("generation input-token budget exceeded")
        if self.generation_output_tokens + output_tokens > self.max_generation_output_tokens:
            raise RuntimeError("generation output-token budget exceeded")
        self.generation_calls += calls
        self.generation_input_tokens += input_tokens
        self.generation_output_tokens += output_tokens

    def reserve_representation(self, tokens: int = 0, calls: int = 1) -> None:
        if calls < 1:
            raise ValueError("calls must be positive")
        if self.representation_calls + calls > self.max_representation_calls:
            raise RuntimeError("representation call budget exceeded")
        self.representation_calls += calls
        self.representation_tokens += tokens

    def reserve_verification(self, calls: int = 1) -> None:
        if self.verification_executions + calls > self.max_verification_executions:
            raise RuntimeError("verification budget exceeded")
        self.verification_executions += calls
