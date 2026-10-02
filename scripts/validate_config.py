#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from graph_reasoning_research.experiments.config import load_yaml, validate_config
cfg=load_yaml(ROOT/"configs/experiments/EXP-001.yaml")
for x in validate_config(cfg): print("INVALID:",x)
sys.exit(1 if validate_config(cfg) else 0)
