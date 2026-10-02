from pathlib import Path
from graph_reasoning_research.experiments.config import load_yaml, validate_config
ROOT=Path(__file__).resolve().parents[1]
def test_initial_config_is_not_real_executable():
    cfg=load_yaml(ROOT/'configs/experiments/EXP-001.yaml'); assert validate_config(cfg)==[]; assert cfg['mode_policy']['real_execution_enabled'] is False
