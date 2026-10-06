from __future__ import annotations

from dataclasses import dataclass

from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.types import CandidateSet, RepresentationBatch


@dataclass
class StructuredReasoningProvider(HashEmbeddingProvider):
    model_id: str = "mock-structured-hash-embedding-v1"
    model_revision: str = "validation-1"
    method: str = "structured_reasoning_hash_embedding"

    def encode(self, candidate_set: CandidateSet) -> RepresentationBatch:
        replaced = tuple(
            candidate.__class__(
                candidate.candidate_id,
                candidate.task_id,
                " ".join(map(str, candidate.metadata.get("reasoning_steps", [candidate.text]))),
                candidate.answer,
                candidate.generator_model_id,
                candidate.seed,
                candidate.generation_config_hash,
                candidate.output_hash,
                candidate.metadata,
            )
            for candidate in candidate_set.candidates
        )
        return super().encode(
            candidate_set.__class__(candidate_set.task_id, replaced, candidate_set.candidate_set_hash)
        )
