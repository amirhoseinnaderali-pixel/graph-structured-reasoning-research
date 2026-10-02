#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    preflight = subprocess.run([sys.executable, str(ROOT / "scripts/preflight.py")], text=True)
    if preflight.returncode != 0:
        print("EXECUTION SMOKE TEST BLOCKED: preflight is not ready.")
        return 1
    print("EXECUTION SMOKE TEST IS DEFINED BUT NOT RUN BY THIS INITIALIZATION TASK.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
