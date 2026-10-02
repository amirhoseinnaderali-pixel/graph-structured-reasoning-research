from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    task_id: str
    text: str
    answer: str | None = None
    generator_id: str = "fixed"
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class CandidateSet:
    task_id: str
    candidates: tuple[Candidate, ...]
    candidate_set_hash: str
    def ids(self) -> tuple[str, ...]:
        return tuple(c.candidate_id for c in self.candidates)

@dataclass(frozen=True)
class RepresentationBatch:
    method: str
    model_id: str
    config_hash: str
    embeddings: Any
    texts: tuple[str, ...]
    representation_hash: str

@dataclass(frozen=True)
class GraphData:
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str, float], ...]
    weighted: bool
    builder: str
    config: dict[str, Any]

@dataclass(frozen=True)
class Selection:
    method: str
    selected_candidate_id: str
    scores: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class CandidateEvaluation:
    candidate_id: str
    objective_result: str
    visible_result: str | None = None
    hidden_result: str | None = None
    failure_class: str | None = None

@dataclass(frozen=True)
class RunRecord:
    experiment_id: str
    run_id: str
    task_id: str
    seed: int
    aggregation_method: str
    representation_method: str
    graph_method: str | None
    candidate_id: str
    selected_candidate_id: str
    objective_result: str
    generation_tokens: int
    representation_tokens: int
    embedding_latency_ms: float
    similarity_latency_ms: float
    representation_latency_ms: float
    graph_construction_latency_ms: float
    graph_scoring_latency_ms: float
    aggregation_latency_ms: float
    verification_latency_ms: float
    candidate_set_hash: str
    representation_hash: str
    graph_stats: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
