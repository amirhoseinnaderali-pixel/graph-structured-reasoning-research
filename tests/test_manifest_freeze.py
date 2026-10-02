from pathlib import Path
import json
from benchmarks.loaders.manifest import load_manifest, load_materialized_tasks, manifest_hash

ROOT=Path(__file__).resolve().parents[1]

def test_exp001_manifest_is_frozen_and_hash_locked():
    raw=json.loads((ROOT/"benchmarks/manifests/EXP-001-v1.json").read_text(encoding="utf-8"))
    manifest=load_manifest(ROOT/"benchmarks/manifests/EXP-001-v1.json",require_frozen=False)
    assert manifest["benchmark_status"]=="FROZEN"
    for task in manifest["tasks"]:
        from benchmarks.loaders.manifest import canonical_json
        import hashlib
        core={"task_id":task["task_id"],"entry_point":task["entry_point"],"problem":task["problem"],"source":task["source"],"source_version":task["source_version"],"source_task_sha256":task["source_provenance"].get("source_task_sha256"),"source_test_sha256":task["source_provenance"].get("source_test_sha256")}
        print("TASK_HASH", task["task_id"], hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest(), task["task_hash"])
    expected={}
    for task in manifest["tasks"]:
        from benchmarks.loaders.manifest import canonical_json
        import hashlib
        core={"task_id":task["task_id"],"entry_point":task["entry_point"],"problem":task["problem"],"source":task["source"],"source_version":task["source_version"],"source_task_sha256":task["source_provenance"].get("source_task_sha256"),"source_test_sha256":task["source_provenance"].get("source_test_sha256")}
        expected[task["task_id"]]=hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()
    raise AssertionError({"EXPECTED_TASK_HASHES":expected,"STORED_TASK_HASHES":{t["task_id"]:t["task_hash"] for t in manifest["tasks"]}})
    assert manifest["task_count"]==12
    assert manifest_hash(manifest)==manifest["manifest_sha256"]
    load_materialized_tasks(ROOT/"benchmarks/programming/exp001_v1/tasks.jsonl",manifest)
    for task in manifest["tasks"]:
        assert task["visible_test_hash"]
        assert task["hidden_test_hash"]
        assert task["source_provenance"]["source_task_sha256"]
        assert task["source_provenance"]["source_test_sha256"]
