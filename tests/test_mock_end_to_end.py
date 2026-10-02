from pathlib import Path
from graph_reasoning_research.experiments.config import load_yaml
from graph_reasoning_research.experiments.runner import run_mock

ROOT=Path(__file__).resolve().parents[1]

def test_mock_end_to_end_is_validation_only(tmp_path):
    cfg=load_yaml(ROOT/"configs/experiments/EXP-001.yaml")
    out=tmp_path/"mock.jsonl"
    rows=run_mock(cfg,out)
    assert rows
    assert all(r["status"]=="validation_only" for r in rows)
    assert out.exists()
