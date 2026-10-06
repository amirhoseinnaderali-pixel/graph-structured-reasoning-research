from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from graph_reasoning_research.types import RunRecord


REQUIRED_FIELDS = {
    "experiment_id",
    "run_id",
    "task_id",
    "seed",
    "aggregation_method",
    "representation_method",
    "representation_config_hash",
    "graph_method",
    "graph_config_hash",
    "candidate_id",
    "selected_candidate_id",
    "objective_result",
    "generation_model_id",
    "generation_config_hash",
    "generation_calls",
    "generation_input_tokens",
    "generation_output_tokens",
    "representation_calls",
    "representation_tokens",
    "embedding_latency_ms",
    "similarity_latency_ms",
    "representation_latency_ms",
    "graph_construction_latency_ms",
    "graph_scoring_latency_ms",
    "aggregation_latency_ms",
    "visible_verification_latency_ms",
    "hidden_verification_latency_ms",
    "candidate_set_hash",
    "representation_hash",
    "similarity_config",
    "graph_stats",
}


def record_to_dict(record: RunRecord) -> dict:
    data = asdict(record)
    data["schema_version"] = "2"
    return data


def validate_record(data: dict) -> list[str]:
    return sorted(REQUIRED_FIELDS - set(data))


def append_jsonl(path: str | Path, record: RunRecord) -> None:
    data = record_to_dict(record)
    missing = validate_record(data)
    if missing:
        raise ValueError(f"invalid run record; missing={missing}")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True) + "\n")
