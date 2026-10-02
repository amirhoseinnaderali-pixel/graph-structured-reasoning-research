from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from graph_reasoning_research.types import CandidateSet, RepresentationBatch


class RepresentationProvider:
    method = "abstract"
    model_id = "UNSET"
    model_revision = "UNSET"
    config: dict = {}

    def encode(self, candidate_set: CandidateSet) -> RepresentationBatch:
        raise NotImplementedError


@dataclass
class HashEmbeddingProvider(RepresentationProvider):
    dimension: int = 32
    model_id: str = "mock-hash-embedding-v1"
    model_revision: str = "validation-1"
    method: str = "hash_embedding"
    config: dict | None = None

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = {
                "method": self.method,
                "model_id": self.model_id,
                "model_revision": self.model_revision,
                "dimension": self.dimension,
                "normalize_embeddings": True,
                "similarity_function": "cosine",
                "status": "validation_only",
            }

    def encode(self, candidate_set: CandidateSet) -> RepresentationBatch:
        rows = []
        for text in [candidate.text for candidate in candidate_set.candidates]:
            row = np.zeros(self.dimension, dtype=np.float64)
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "little") % self.dimension
                row[index] += 1.0 if digest[4] % 2 else -1.0
            norm = np.linalg.norm(row)
            if norm:
                row /= norm
            rows.append(row)
        matrix = np.vstack(rows) if rows else np.empty((0, self.dimension))
        config_hash = hashlib.sha256(
            json.dumps(self.config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        representation_hash = hashlib.sha256(matrix.tobytes()).hexdigest()
        return RepresentationBatch(
            self.method,
            self.model_id,
            self.model_revision,
            config_hash,
            matrix,
            tuple(candidate.text for candidate in candidate_set.candidates),
            representation_hash,
        )
