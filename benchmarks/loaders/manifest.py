from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class BenchmarkNotFrozenError(RuntimeError):
    pass


def canonical_manifest_payload(data: dict[str, Any]) -> bytes:
    payload = dict(data)
    payload.pop("manifest_hash", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def manifest_hash(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_manifest_payload(data)).hexdigest()


def load_manifest(path: str | Path, *, require_frozen: bool = True) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if require_frozen and data.get("benchmark_status") != "FROZEN":
        raise BenchmarkNotFrozenError(f"Benchmark is not frozen: {data.get('benchmark_status', 'MISSING')}")
    if data.get("task_count") != len(data.get("tasks", [])):
        raise ValueError("task_count does not match tasks length")
    if require_frozen:
        missing = [task["task_id"] for task in data.get("tasks", []) if validate_task_entry(task)]
        if missing:
            raise ValueError(f"frozen manifest has incomplete tasks: {missing[:5]}")
        expected = data.get("manifest_hash")
        if expected != manifest_hash(data):
            raise ValueError("manifest_hash does not match canonical manifest content")
    return data


def validate_task_entry(task: dict[str, Any]) -> list[str]:
    required = ["task_id", "task_hash", "visible_test_hash", "hidden_test_hash"]
    return [key for key in required if not task.get(key)]
