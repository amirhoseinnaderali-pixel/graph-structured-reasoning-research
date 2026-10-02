#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_reasoning_research.experiments.config import load_yaml, validate_config

config = load_yaml(ROOT / "configs/experiments/EXP-001.yaml")
failures = validate_config(config)
for failure in failures:
    print("INVALID:", failure)
sys.exit(1 if failures else 0)
