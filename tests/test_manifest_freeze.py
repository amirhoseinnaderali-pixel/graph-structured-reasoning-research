from pathlib import Path

from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks, manifest_hash

ROOT = Path(__file__).resolve().parents[1]

def test_exp001_manifest_is_frozen_and_hash_locked():
    manifest = load_manifest(ROOT / "benchmarks/manifests/EXP-001-v1.json", require_frozen=True)
    assert manifest["benchmark_status"] == "FROZEN"
    assert manifest["task_count"] == 12
    assert manifest_hash(manifest) == manifest["manifest_sha256"]
    load_materialized_tasks(ROOT / "benchmarks/programming/exp001_v1/tasks.jsonl", manifest)
    for task in manifest["tasks"]:
        assert task["visible_test_hash"]
        assert task["hidden_test_hash"]
        assert task["source_provenance"]["source_task_sha256"]
        assert task["source_provenance"]["source_test_sha256"]
