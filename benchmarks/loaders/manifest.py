from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class BenchmarkNotFrozenError(RuntimeError):
    pass


def load_manifest(path: str | Path, *, require_frozen: bool = True) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if require_frozen and data.get("benchmark_status") != "FROZEN":
        raise BenchmarkNotFrozenError(
            f"Benchmark is not frozen: {data.get('benchmark_status', 'MISSING')}"
        )
    if data.get("task_count") != len(data.get("tasks", [])):
        raise ValueError("task_count does not match tasks length")
    if require_frozen:
        missing = [t["task_id"] for t in data.get("tasks", []) if validate_task_entry(t)]
        if missing:
            raise ValueError(f"frozen manifest has incomplete tasks: {missing[:5]}")
    return data


def manifest_hash(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_task_entry(task: dict[str, Any]) -> list[str]:
    required = ["task_id", "task_hash", "visible_test_hash", "hidden_test_hash"]
    return [k for k in required if not task.get(k)]
