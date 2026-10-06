from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_config(config: dict[str, Any]) -> list[str]:
    failures = []
    if config.get("experiment_id") != "EXP-001":
        failures.append("experiment_id must be EXP-001")
    if config.get("status") != "NOT_EXECUTED":
        failures.append("EXP-001 config status must remain NOT_EXECUTED")
    if config.get("mode_policy", {}).get("real_execution_enabled") is not False:
        failures.append("real execution must remain disabled in the initial repository state")
    if not config.get("seeds"):
        failures.append("explicit seeds are required")
    return failures
