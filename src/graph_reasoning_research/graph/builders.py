from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from graph_reasoning_research.types import GraphData


def graph_config_hash(config: dict) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class GraphBuilder:
    name: str
    threshold: float | None = None
    k: int | None = None
    weighted: bool = True

    def build(self, node_ids: tuple[str, ...], similarity: np.ndarray) -> GraphData:
        n = len(node_ids)
        if similarity.shape != (n, n):
            raise ValueError("similarity shape must match node count")
        config = {
            "builder": self.name,
            "threshold": self.threshold,
            "k": self.k,
            "weighted": self.weighted,
            "similarity_function": "cosine",
        }
        edges: set[tuple[int, int]] = set()
        if self.name == "threshold":
            if self.threshold is None:
                raise ValueError("threshold graph requires threshold")
            for i in range(n):
                for j in range(i + 1, n):
                    if similarity[i, j] >= self.threshold:
                        edges.add((i, j))
        elif self.name == "knn":
            if self.k is None or self.k < 1:
                raise ValueError("kNN graph requires k >= 1")
            if self.k >= n and n > 1:
                raise ValueError("k must be smaller than node count")
            for i in range(n):
                order = np.argsort(-similarity[i], kind="stable")
                added = 0
                for j_raw in order:
                    j = int(j_raw)
                    if j == i:
                        continue
                    edges.add(tuple(sorted((i, j))))
                    added += 1
                    if added >= self.k:
                        break
        else:
            raise ValueError(f"unknown graph builder: {self.name}")
        materialized = tuple(
            (node_ids[i], node_ids[j], float(similarity[i, j]) if self.weighted else 1.0)
            for i, j in sorted(edges)
        )
        cfg_hash = graph_config_hash(config)
        return GraphData(node_ids, materialized, self.weighted, self.name, config, cfg_hash)


def threshold_graph(node_ids, similarity, threshold, weighted):
    return GraphBuilder("threshold", threshold=float(threshold), weighted=bool(weighted)).build(
        node_ids, similarity
    )


def knn_graph(node_ids, similarity, k, weighted):
    return GraphBuilder("knn", k=int(k), weighted=bool(weighted)).build(node_ids, similarity)
