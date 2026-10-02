from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class BenchmarkNotFrozenError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_manifest_payload(data: dict[str, Any]) -> bytes:
    payload = dict(data)
    payload.pop("manifest_sha256", None)
    return canonical_json(payload).encode("utf-8")


def manifest_hash(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_manifest_payload(data)).hexdigest()


def _task_core(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "entry_point": task["entry_point"],
        "problem": task["problem"],
        "source": task["source"],
        "source_version": task["source_version"],
        "source_task_sha256": task["source_provenance"].get("source_task_sha256"),
        "source_test_sha256": task["source_provenance"].get("source_test_sha256"),
    }


def _verify_hash(name: str, expected: str, value: Any) -> None:
    actual = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    if expected != actual:
        raise ValueError(f"{name} mismatch: expected {expected}, got {actual}")


def validate_task_entry(task: dict[str, Any]) -> list[str]:
    required = {
        "task_id", "entry_point", "problem", "candidate_generation_prompt_view",
        "visible_tests", "hidden_tests", "provenance", "source", "source_version",
        "task_hash", "visible_test_hash", "hidden_test_hash", "source_provenance",
    }
    return sorted(required - set(task))


def load_manifest(path: str | Path, *, require_frozen: bool = True) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if require_frozen and data.get("benchmark_status") != "FROZEN":
        raise BenchmarkNotFrozenError(f"Benchmark is not frozen: {data.get('benchmark_status', 'MISSING')}")
    if data.get("task_count") != len(data.get("tasks", [])) or not data.get("tasks"):
        raise ValueError("benchmark task_count must match a non-empty explicit task set")
    if require_frozen:
        expected_manifest_hash = data.get("manifest_sha256")
        if not expected_manifest_hash or expected_manifest_hash != manifest_hash(data):
            raise ValueError("manifest_sha256 does not match canonical manifest content")
        for task in data["tasks"]:
            missing = validate_task_entry(task)
            if missing:
                raise ValueError(f"task {task.get('task_id')} missing fields: {missing}")
            if hashlib.sha256(canonical_json(_task_core(task)).encode("utf-8")).hexdigest() != task["task_hash"]:
                raise ValueError(f"task hash mismatch: {task['task_id']}")
            _verify_hash(f"visible_test_hash for {task['task_id']}", task["visible_test_hash"], task["visible_tests"])
            _verify_hash(f"hidden_test_hash for {task['task_id']}", task["hidden_test_hash"], task["hidden_tests"])
            if task["visible_tests"] == task["hidden_tests"]:
                raise ValueError(f"visible/hidden tests are identical for {task['task_id']}")
            if "hidden_tests" in task["candidate_generation_prompt_view"] or "hidden" in task["candidate_generation_prompt_view"].lower():
                raise ValueError(f"candidate prompt contains hidden-test material for {task['task_id']}")
    return data


def load_materialized_tasks(path: str | Path, manifest: dict[str, Any]) -> None:
    materialized = Path(path)
    actual = hashlib.sha256(materialized.read_bytes()).hexdigest()
    if actual != manifest.get("materialization_sha256"):
        raise ValueError(
            f"materialized benchmark hash mismatch: expected {manifest.get('materialization_sha256')}, got {actual}"
        )
    rows = [json.loads(line) for line in materialized.read_text(encoding="utf-8").splitlines() if line.strip()]
    expected_ids = [task["task_id"] for task in manifest["tasks"]]
    observed_ids = [row.get("id") for row in rows]
    if observed_ids != expected_ids:
        raise ValueError("materialized benchmark task order/identity mismatch")
    for row, task in zip(rows, manifest["tasks"]):
        if row.get("problem") != task["problem"] or row.get("entry_point") != task["entry_point"]:
            raise ValueError(f"materialized task content mismatch: {task['task_id']}")
        if row.get("tests", {}).get("visible") != task["visible_tests"] or row.get("tests", {}).get("hidden") != task["hidden_tests"]:
            raise ValueError(f"materialized test split mismatch: {task['task_id']}")
