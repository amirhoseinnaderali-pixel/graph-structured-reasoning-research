from pathlib import Path
from graph_reasoning_research.experiments.config import load_yaml, validate_config, validate_bundle

ROOT=Path(__file__).resolve().parents[1]

def test_frozen_experiment_contract():
    cfg=load_yaml(ROOT/"configs/experiments/EXP-001.yaml")
    assert validate_config(cfg)==[]
    assert cfg["mode_policy"]["real_execution_enabled"] is True
    assert cfg["mode_policy"]["mock_allowed"] is True

def test_frozen_bundle_has_required_external_contracts():
    cfg=load_yaml(ROOT/"configs/experiments/EXP-001.yaml")
    failures=validate_bundle(ROOT,cfg)
    assert not [x for x in failures if "benchmark" in x.lower()]
    assert not [x for x in failures if "candidate model" in x.lower()]
    assert not [x for x in failures if "representation" in x.lower()]
    assert not [x for x in failures if "graph config" in x.lower()]
    assert not [x for x in failures if "budget config" in x.lower()]
    assert not [x for x in failures if "runtime config" in x.lower()]
