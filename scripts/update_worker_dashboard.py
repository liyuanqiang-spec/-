#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    script = ROOT / "scripts" / "refresh_visible_status.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(ROOT), "--quiet"],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode == 0:
        print(ROOT / "WORKER_DASHBOARD.md")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
