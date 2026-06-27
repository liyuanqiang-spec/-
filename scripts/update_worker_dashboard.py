#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.codex_quant.dashboard import update_dashboard  # noqa: E402


def main() -> int:
    path = update_dashboard(ROOT)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
