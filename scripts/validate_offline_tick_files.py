#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.codex_quant.config import (  # noqa: E402
    BACKTEST_BASELINE_REPORT,
    DEFAULT_MAX_SPREAD_PCT,
    DEFAULT_MIN_VOLUME,
    QUANT_SYSTEM_GAP_REPORT,
    SAMPLE_CONTRACTS,
    TICK_FILE_SMOKE_REPORT,
    TICK_REPLAY_FIXTURE,
    QUOTE_REPLAY_FIXTURE,
)
from src.codex_quant.contract_scanner import load_contracts, scan_contracts  # noqa: E402
from src.codex_quant.quant_baseline import _rel  # noqa: E402
from src.codex_quant.quote_replay import replay_vertical_spreads  # noqa: E402
from src.codex_quant.spread_calculator import calculate_vertical_spreads  # noqa: E402
from src.codex_quant.tick_replay_adapter import (  # noqa: E402
    TickReplayLoadResult,
    load_tick_snapshots,
    write_sanitized_tick_fixture_from_quote_replay,
)


HISTORICAL_TICK_CANDIDATES = (
    Path("DATA/raw/ticks.csv"),
    Path("DATA/raw/tick.csv"),
    Path("DATA/raw/silver_option_ticks.csv"),
    Path("DATA/raw/option_ticks.csv"),
    Path("data/raw/ticks.csv"),
    Path("data/raw/tick.csv"),
    Path("data/raw/silver_option_ticks.csv"),
    Path("data/raw/option_ticks.csv"),
)


def _find_historical_tick_file(root: Path) -> Path | None:
    for rel in HISTORICAL_TICK_CANDIDATES:
        path = root / rel
        if path.is_file():
            return path
    return None


def _status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def _write_report(
    path: Path,
    result: TickReplayLoadResult,
    replay_count: int,
    replay_fills: int,
    replay_incomplete: int,
    fixture_rows_written: int,
    historical_blocker: str,
) -> None:
    lines = [
        "# TASK-011A Offline Tick File Smoke Report",
        "",
        "结论：离线 tick parser 和 replay adapter 已跑通。仓库内没有发现真实历史 tick CSV；本次使用 TASK-010 的本地多快照 quote fixture 派生了一个极小脱敏 tick fixture，只用于验证字段映射、schema 检查和 replay 适配，不代表真实行情或真实成交。",
        "",
        "## Safety Boundary",
        "",
        "- Current phase: `PHASE_1_SIMULATION_ONLY`.",
        "- Data scope: repository-local `DATA/` fixture files only.",
        "- Not used: real trading account connection, real order placement, order cancellation, fund transfer, original-data deletion, secrets, paid API, or dangerous sandbox.",
        "",
        "## Source Selection",
        "",
        f"- Historical tick source blocker: {historical_blocker}",
        f"- Smoke tick source: `{_rel(result.source_path)}`.",
        f"- Rows written to smoke fixture: {fixture_rows_written}.",
        f"- Source rows read: {result.source_row_count}.",
        "",
        "## Required Field Check",
        "",
        "| Required field | Mapped column | Status |",
        "|---|---|---:|",
    ]
    for check in result.schema_checks:
        lines.append(
            f"| `{check.canonical_field}` | `{check.mapped_column or 'MISSING'}` | {_status(check.present)} |"
        )

    lines.extend(
        [
            "",
            "## Parser Result",
            "",
            f"- Parser status: `{_status(result.ok)}`.",
            f"- Replay snapshots loaded: {result.snapshot_count}.",
            f"- Symbols loaded: {', '.join(result.symbols) if result.symbols else 'None'}.",
            f"- Missing required fields: {', '.join(result.missing_required_fields) if result.missing_required_fields else 'None'}.",
            f"- Unsupported symbols: {', '.join(result.unsupported_symbols) if result.unsupported_symbols else 'None'}.",
            f"- Invalid rows: {len(result.invalid_rows)}.",
        ]
    )
    if result.invalid_rows:
        lines.extend(f"- {item}" for item in result.invalid_rows[:20])

    lines.extend(
        [
            "",
            "## Replay Adapter Result",
            "",
            f"- Candidate replays produced: {replay_count}.",
            f"- First-leg fills: {replay_fills}.",
            f"- Incomplete legs: {replay_incomplete}.",
            f"- Refreshed quant reports: `{_rel(QUANT_SYSTEM_GAP_REPORT)}`, `{_rel(BACKTEST_BASELINE_REPORT)}`.",
            "",
            "## Exact Local-File Blocker",
            "",
            f"- {historical_blocker}",
            "- Current validation therefore proves only offline parser/replay compatibility on repository-local sanitized data, not historical-market coverage.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(root: Path, source: Path | None, report_path: Path) -> dict[str, int | str | bool]:
    historical_blocker = "not checked"
    fixture_rows_written = 0
    if source is None:
        historical_source = _find_historical_tick_file(root)
        if historical_source:
            source = historical_source
            historical_blocker = "none; historical tick file found inside repository data folders"
        else:
            checked = ", ".join(path.as_posix() for path in HISTORICAL_TICK_CANDIDATES)
            historical_blocker = f"missing file: no historical tick CSV found under checked repository paths: {checked}"
            fixture_rows_written = write_sanitized_tick_fixture_from_quote_replay(
                QUOTE_REPLAY_FIXTURE,
                SAMPLE_CONTRACTS,
                TICK_REPLAY_FIXTURE,
            )
            source = TICK_REPLAY_FIXTURE

    result = load_tick_snapshots(source, SAMPLE_CONTRACTS)
    contracts = scan_contracts(load_contracts(SAMPLE_CONTRACTS), DEFAULT_MIN_VOLUME, DEFAULT_MAX_SPREAD_PCT)
    candidates = calculate_vertical_spreads(contracts)
    replay_results = replay_vertical_spreads(candidates, list(result.snapshots)) if result.ok else []
    _write_report(
        report_path,
        result,
        replay_count=len(replay_results),
        replay_fills=sum(1 for item in replay_results if item.first_leg_filled),
        replay_incomplete=sum(1 for item in replay_results if item.incomplete_leg),
        fixture_rows_written=fixture_rows_written,
        historical_blocker=historical_blocker,
    )
    return {
        "ok": result.ok,
        "source": _rel(source),
        "snapshots": result.snapshot_count,
        "replays": len(replay_results),
        "report": _rel(report_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate offline local tick CSV files against replay schema.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--source", default="")
    parser.add_argument("--report", default=str(TICK_FILE_SMOKE_REPORT))
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    source = Path(args.source).resolve() if args.source else None
    report_path = Path(args.report).resolve()
    result = run(root, source, report_path)
    print(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
