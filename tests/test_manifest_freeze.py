from pathlib import Path
import hashlib

from benchmarks.loaders.manifest import load_manifest, manifest_hash

ROOT = Path(__file__).resolve().parents[1]

def test_exp001_manifest_is_frozen_and_hash_locked():
    manifest = load_manifest(ROOT / "benchmarks/manifests/EXP-001-v1.json", require_frozen=False)
    materialized = ROOT / "benchmarks/programming/exp001_v1/tasks.jsonl"
    print("PYTHON_MANIFEST_HASH", manifest_hash(manifest))
    print("STORED_MANIFEST_HASH", manifest["manifest_sha256"])
    print("MATERIALIZED_SHA", hashlib.sha256(materialized.read_bytes()).hexdigest())
    raise AssertionError({
        "EXPECTED_MANIFEST_HASH": manifest_hash(manifest),
        "STORED_MANIFEST_HASH": manifest["manifest_sha256"],
        "MATERIALIZED_SHA": hashlib.sha256(materialized.read_bytes()).hexdigest(),
    })
