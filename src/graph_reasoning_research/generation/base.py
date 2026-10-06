from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from graph_reasoning_research.types import Candidate, CandidateSet


def generation_config_hash(config: dict) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def candidate_output_hash(text: str, answer: str | None) -> str:
    payload = json.dumps({"text": text, "answer": answer}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def candidate_set_hash(candidates: list[Candidate] | tuple[Candidate, ...]) -> str:
    manifest = [
        {
            "candidate_id": c.candidate_id,
            "task_id": c.task_id,
            "generator_model_id": c.generator_model_id,
            "seed": c.seed,
            "generation_config_hash": c.generation_config_hash,
            "output_hash": c.output_hash,
        }
        for c in candidates
    ]
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def assert_same_candidate_set(*candidate_sets: CandidateSet) -> str:
    if not candidate_sets:
        raise ValueError("at least one candidate set is required")
    expected = candidate_sets[0].candidate_set_hash
    expected_manifest = candidate_sets[0].manifest()
    for idx, candidate_set in enumerate(candidate_sets[1:], start=1):
        if candidate_set.candidate_set_hash != expected or candidate_set.manifest() != expected_manifest:
            raise ValueError(
                f"candidate-set equivalence violated at index {idx}: "
                f"expected={expected}, observed={candidate_set.candidate_set_hash}"
            )
    return expected


class CandidateGenerator:
    model_id = "UNSET"
    generation_config: dict = {}

    def generate(self, task_id: str, problem: str, n: int, seed: int) -> CandidateSet:
        raise NotImplementedError


@dataclass
class MockCandidateGenerator(CandidateGenerator):
    model_id: str = "mock-generator-v1"
    generation_config: dict = None

    def __post_init__(self) -> None:
        if self.generation_config is None:
            self.generation_config = {"temperature": 0.0, "max_tokens": 128, "mode": "validation_only"}

    def generate(self, task_id: str, problem: str, n: int, seed: int) -> CandidateSet:
        if n < 1:
            raise ValueError("n must be positive")
        cfg_hash = generation_config_hash(self.generation_config)
        candidates: list[Candidate] = []
        for i in range(n):
            variant = (i + seed) % n
            text = f"Mock solution {i} for {problem}. Reasoning variant {variant}."
            answer = str(variant % 2)
            candidates.append(
                Candidate(
                    candidate_id=f"{task_id}-c{i}",
                    task_id=task_id,
                    text=text,
                    answer=answer,
                    generator_model_id=self.model_id,
                    seed=seed,
                    generation_config_hash=cfg_hash,
                    output_hash=candidate_output_hash(text, answer),
                )
            )
        return CandidateSet(task_id, tuple(candidates), candidate_set_hash(candidates))
