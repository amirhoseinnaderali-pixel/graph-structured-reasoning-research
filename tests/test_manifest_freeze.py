from pathlib import Path
import hashlib
import json
from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks, manifest_hash, canonical_json

ROOT = Path(__file__).resolve().parents[1]

def test_exp001_manifest_is_frozen_and_hash_locked():
    manifest = load_manifest(ROOT / "benchmarks/manifests/EXP-001-v1.json", require_frozen=False)
    expected = {}
    for task in manifest["tasks"]:
        core = {
            "task_id": task["task_id"],
            "entry_point": task["entry_point"],
            "problem": task["problem"],
            "source": task["source"],
            "source_version": task["source_version"],
            "source_task_sha256": task["source_provenance"].get("source_task_sha256"),
            "source_test_sha256": task["source_provenance"].get("source_test_sha256"),
        }
        expected[task["task_id"]] = {
            "task_hash": hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest(),
            "visible_test_hash": hashlib.sha256(canonical_json(task["visible_tests"]).encode("utf-8")).hexdigest(),
            "hidden_test_hash": hashlib.sha256(canonical_json(task["hidden_tests"]).encode("utf-8")).hexdigest(),
        }
    print(json.dumps(expected, sort_keys=True))
    print("PYTHON_MANIFEST_HASH", manifest_hash(manifest))
    print("MATERIALIZED_SHA", hashlib.sha256((ROOT / "benchmarks/programming/exp001_v1/tasks.jsonl").read_bytes()).hexdigest())
    raise AssertionError(expected)
