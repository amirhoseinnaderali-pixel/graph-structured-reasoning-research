from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass

import numpy as np

from graph_reasoning_research.types import CandidateSet, RepresentationBatch

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|[^\s\w]")


@dataclass
class FeatureHashTfidfProvider:
    dimension: int = 2048
    model_id: str = "feature-hash-tfidf-v1"
    model_revision: str = "algorithm-spec-1"
    method: str = "feature_hash_tfidf"

    def _bucket(self, token: str) -> int:
        return int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:4], "big") % self.dimension

    def encode(self, candidate_set: CandidateSet) -> RepresentationBatch:
        token_lists = [[token.lower() for token in TOKEN_RE.findall(c.text)] for c in candidate_set.candidates]
        document_frequency: dict[str, int] = {}
        for tokens in token_lists:
            for token in set(tokens):
                document_frequency[token] = document_frequency.get(token, 0) + 1

        n_docs = max(len(token_lists), 1)
        matrix = np.zeros((len(token_lists), self.dimension), dtype=np.float64)
        for row_idx, tokens in enumerate(token_lists):
            counts: dict[str, int] = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
            for token, count in counts.items():
                tf = count / max(len(tokens), 1)
                idf = math.log((1.0 + n_docs) / (1.0 + document_frequency[token])) + 1.0
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                matrix[row_idx, self._bucket(token)] += sign * tf * idf
            norm = np.linalg.norm(matrix[row_idx])
            if norm:
                matrix[row_idx] /= norm

        config = {
            "method": self.method,
            "model_id": self.model_id,
            "model_revision": self.model_revision,
            "dimension": self.dimension,
            "normalize_embeddings": True,
            "similarity_function": "cosine",
            "tokenization": "python_identifier_and_text_v1",
            "hashing": "sha256_low32_v1",
            "fit_scope": "candidate_set_only",
        }
        config_hash = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        representation_hash = hashlib.sha256(
            candidate_set.candidate_set_hash.encode("utf-8") + matrix.tobytes()
        ).hexdigest()
        return RepresentationBatch(
            self.method,
            self.model_id,
            self.model_revision,
            config_hash,
            matrix,
            tuple(c.text for c in candidate_set.candidates),
            representation_hash,
        )
