from __future__ import annotations
from dataclasses import dataclass
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.types import CandidateSet, RepresentationBatch
@dataclass
class StructuredReasoningProvider(HashEmbeddingProvider):
    model_id:str='mock-structured-hash-embedding-v1'; method:str='structured_reasoning_hash_embedding'
    def encode(self,candidate_set:CandidateSet)->RepresentationBatch:
        replaced=tuple(c.__class__(c.candidate_id,c.task_id,' '.join(map(str,c.metadata.get('reasoning_steps',[c.text]))),c.answer,c.generator_id,c.metadata) for c in candidate_set.candidates)
        return super().encode(candidate_set.__class__(candidate_set.task_id,replaced,candidate_set.candidate_set_hash))
