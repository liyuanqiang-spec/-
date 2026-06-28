from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .backtester import run_first_complete_simulation, run_simple_backtest
from .config import (
    BACKTEST_BASELINE_REPORT,
    DEFAULT_MAX_SPREAD_PCT,
    DEFAULT_MIN_VOLUME,
    PROJECT_ROOT,
    QUANT_BASELINE_REPLAY_CSV,
    QUANT_SYSTEM_GAP_REPORT,
    QUOTE_REPLAY_FIXTURE,
    SAMPLE_CONTRACTS,
    TRADING_MODE,
)
from .contract_scanner import load_contracts, scan_contracts
from .low_liquidity_scanner import scan_low_liquidity_contracts
from .quote_replay import QuoteReplayResult, QuoteSnapshot, load_quote_snapshots, replay_vertical_spreads
from .risk_control import check_research_risk
from .schemas import OptionContract, SimulationSummary, SpreadCandidate, SpreadSimulation
from .spread_calculator import calculate_vertical_spreads


STATE_DONE = ("IDLE", "FOUND", "PENDING_FIRST_LEG", "FIRST_LEG_FILLED", "HEDGING_SECOND_LEG", "DONE")
STATE_FAILED = ("IDLE", "FOUND", "PENDING_FIRST_LEG", "FAILED", "COOLDOWN")


@dataclass(frozen=True)
class TimeValueRow:
    symbol: str
    underlying: str
    expiry: str
    option_type: str
    strike: float
    bid: float
    ask: float
    mid: float
    inferred_underlying: float
    intrinsic: float
    bid_time_value: float
    mid_time_value: float
    ask_time_value: float
    spread_pct: float
    parity_deviation: float | None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ScoredSpread:
    candidate: SpreadCandidate
    simulation: SpreadSimulation
    expected_edge: float
    fill_probability: float
    liquidity_score: float
    risk_score: float
    second_leg_cost_estimate: float
    max_adverse_move: float
    total_score: float
    state_path: tuple[str, ...]
    incomplete_leg: bool


@dataclass(frozen=True)
class QuantBaselineResult:
    raw_contracts: list[OptionContract]
    scanned_contracts: list[OptionContract]
    low_liquidity_count: int
    time_value_rows: list[TimeValueRow]
    candidates: list[SpreadCandidate]
    simulations: list[SpreadSimulation]
    scored_spreads: list[ScoredSpread]
    quote_snapshots: list[QuoteSnapshot]
    quote_replay_results: list[QuoteReplayResult]
    summary: SimulationSummary
    backtest: dict[str, float | int | str]
    risk_issues: list[str]
    replay_csv: Path


def infer_underlying_by_expiry(contracts: list[OptionContract]) -> dict[tuple[str, str], float]:
    by_key: dict[tuple[str, str, float], dict[str, OptionContract]] = {}
    for contract in contracts:
        by_key.setdefault((contract.underlying, contract.expiry, contract.strike), {})[
            contract.option_type
        ] = contract

    inferred: dict[tuple[str, str], list[float]] = {}
    fallback: dict[tuple[str, str], list[float]] = {}
    for (underlying, expiry, strike), pair in by_key.items():
        key = (underlying, expiry)
        fallback.setdefault(key, []).append(strike)
        if "C" in pair and "P" in pair:
            level = strike + pair["C"].mid - pair["P"].mid
            inferred.setdefault(key, []).append(level)

    levels: dict[tuple[str, str], float] = {}
    for key, values in fallback.items():
        source = inferred.get(key) or values
        levels[key] = round(sum(source) / len(source), 4)
    return levels


def build_time_value_radar(contracts: list[OptionContract]) -> list[TimeValueRow]:
    underlying_levels = infer_underlying_by_expiry(contracts)
    pairs: dict[tuple[str, str, float], dict[str, OptionContract]] = {}
    for contract in contracts:
        pairs.setdefault((contract.underlying, contract.expiry, contract.strike), {})[
            contract.option_type
        ] = contract

    rows: list[TimeValueRow] = []
    for contract in contracts:
        underlying = underlying_levels[(contract.underlying, contract.expiry)]
        if contract.option_type == "C":
            intrinsic = max(0.0, underlying - contract.strike)
        else:
            intrinsic = max(0.0, contract.strike - underlying)

        pair = pairs.get((contract.underlying, contract.expiry, contract.strike), {})
        parity_deviation: float | None = None
        if "C" in pair and "P" in pair:
            parity_deviation = round(pair["C"].mid - pair["P"].mid - (underlying - contract.strike), 4)

        bid_tv = round(contract.bid - intrinsic, 4)
        mid_tv = round(contract.mid - intrinsic, 4)
        ask_tv = round(contract.ask - intrinsic, 4)
        flags: list[str] = []
        if bid_tv < 0:
            flags.append("NEGATIVE_BID_TIME_VALUE")
        if mid_tv < 0:
            flags.append("NEGATIVE_MID_TIME_VALUE")
        if contract.spread_pct >= 0.15:
            flags.append("WIDE_SPREAD")
        if parity_deviation is not None and abs(parity_deviation) > 2.0:
            flags.append("PARITY_DEVIATION")
        if not flags:
            flags.append("OK")

        rows.append(
            TimeValueRow(
                symbol=contract.symbol,
                underlying=contract.underlying,
                expiry=contract.expiry,
                option_type=contract.option_type,
                strike=contract.strike,
                bid=contract.bid,
                ask=contract.ask,
                mid=round(contract.mid, 4),
                inferred_underlying=underlying,
                intrinsic=round(intrinsic, 4),
                bid_time_value=bid_tv,
                mid_time_value=mid_tv,
                ask_time_value=ask_tv,
                spread_pct=round(contract.spread_pct, 4),
                parity_deviation=parity_deviation,
                flags=tuple(flags),
            )
        )
    return sorted(rows, key=lambda item: (item.expiry, item.option_type, item.strike))


def score_spreads(
    candidates: list[SpreadCandidate],
    simulations: list[SpreadSimulation],
) -> list[ScoredSpread]:
    by_pair = {
        (simulation.candidate.long_symbol, simulation.candidate.short_symbol): simulation
        for simulation in simulations
    }
    scored: list[ScoredSpread] = []
    for candidate in candidates:
        simulation = by_pair.get((candidate.long_symbol, candidate.short_symbol))
        if simulation is None:
            continue
        incomplete_leg = simulation.passive_fill_probability < 0.5 or not simulation.accepted
        second_leg_cost = round(simulation.hedge_slippage + 0.2, 4)
        max_adverse_move = round(simulation.hedge_slippage + max(0.0, -simulation.simulated_edge), 4)
        expected_edge = round(
            simulation.simulated_edge * simulation.passive_fill_probability - second_leg_cost,
            4,
        )
        liquidity_score = round(min(candidate.liquidity_score / 100.0, 100.0), 4)
        risk_score = round(
            len(simulation.risk_flags) * 12.5
            + (1.0 - simulation.passive_fill_probability) * 20
            + max(0.0, simulation.hedge_slippage - 1.0) * 5,
            4,
        )
        total_score = round(expected_edge * 10 + liquidity_score - risk_score, 4)
        state_path = STATE_FAILED if incomplete_leg else STATE_DONE
        scored.append(
            ScoredSpread(
                candidate=candidate,
                simulation=simulation,
                expected_edge=expected_edge,
                fill_probability=simulation.passive_fill_probability,
                liquidity_score=liquidity_score,
                risk_score=risk_score,
                second_leg_cost_estimate=second_leg_cost,
                max_adverse_move=max_adverse_move,
                total_score=total_score,
                state_path=state_path,
                incomplete_leg=incomplete_leg,
            )
        )
    return sorted(scored, key=lambda item: item.total_score, reverse=True)


def write_replay_csv(
    path: Path,
    scored: list[ScoredSpread],
    replay_results: list[QuoteReplayResult],
) -> None:
    replay_by_pair = {
        (result.candidate.long_symbol, result.candidate.short_symbol): result
        for result in replay_results
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            lineterminator="\n",
            fieldnames=[
                "rank",
                "long_symbol",
                "short_symbol",
                "state_path",
                "replay_state_path",
                "first_leg_symbol",
                "first_leg_action",
                "hedge_leg_symbol",
                "hedge_action",
                "first_leg_timeout_seconds",
                "elapsed_seconds",
                "first_leg_filled",
                "timed_out",
                "stale_quote_count",
                "reprice_count",
                "passive_fill_probability",
                "replay_passive_fill_probability",
                "replay_passive_limit_price",
                "simulated_edge",
                "expected_edge",
                "second_leg_cost_estimate",
                "max_adverse_move",
                "second_leg_adverse_move",
                "total_score",
                "accepted",
                "incomplete_leg",
                "replay_incomplete_leg",
                "risk_flags",
                "replay_risk_flags",
            ],
        )
        writer.writeheader()
        for rank, item in enumerate(scored, start=1):
            replay = replay_by_pair.get((item.candidate.long_symbol, item.candidate.short_symbol))
            writer.writerow(
                {
                    "rank": rank,
                    "long_symbol": item.candidate.long_symbol,
                    "short_symbol": item.candidate.short_symbol,
                    "state_path": ">".join(item.state_path),
                    "replay_state_path": ">".join(replay.state_path) if replay else "",
                    "first_leg_symbol": replay.first_leg_symbol if replay else "",
                    "first_leg_action": replay.first_leg_action if replay else "",
                    "hedge_leg_symbol": replay.hedge_leg_symbol if replay else "",
                    "hedge_action": replay.hedge_action if replay else "",
                    "first_leg_timeout_seconds": replay.first_leg_timeout_seconds if replay else "",
                    "elapsed_seconds": replay.elapsed_seconds if replay else "",
                    "first_leg_filled": replay.first_leg_filled if replay else "",
                    "timed_out": replay.timed_out if replay else "",
                    "stale_quote_count": replay.stale_quote_count if replay else "",
                    "reprice_count": replay.reprice_count if replay else "",
                    "passive_fill_probability": item.fill_probability,
                    "replay_passive_fill_probability": replay.passive_fill_probability if replay else "",
                    "replay_passive_limit_price": replay.passive_limit_price if replay else "",
                    "simulated_edge": item.simulation.simulated_edge,
                    "expected_edge": item.expected_edge,
                    "second_leg_cost_estimate": item.second_leg_cost_estimate,
                    "max_adverse_move": item.max_adverse_move,
                    "second_leg_adverse_move": replay.second_leg_adverse_move if replay else "",
                    "total_score": item.total_score,
                    "accepted": item.simulation.accepted,
                    "incomplete_leg": item.incomplete_leg,
                    "replay_incomplete_leg": replay.incomplete_leg if replay else "",
                    "risk_flags": ",".join(item.simulation.risk_flags),
                    "replay_risk_flags": ",".join(replay.risk_flags) if replay else "",
                }
            )


def _rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _flags(flags: tuple[str, ...]) -> str:
    return ", ".join(flags) if flags else "None"


def can_answer_key_question(result: QuantBaselineResult) -> str:
    if not result.scored_spreads:
        return "不能；当前没有可回放价差。"
    if result.quote_replay_results:
        filled = sum(1 for item in result.quote_replay_results if item.first_leg_filled)
        incomplete = sum(1 for item in result.quote_replay_results if item.incomplete_leg)
        return (
            "只能做仓库 fixture 级 replay 判断，不能做统计结论；当前多快照样本回放 "
            f"{len(result.quote_replay_results)} 组候选，第一腿成交 {filled} 组，不完整腿 {incomplete} 组，"
            f"静态平均模拟改善 {result.summary.average_simulated_edge:g} 点。"
        )
    if result.summary.reliability == "LOW_SAMPLE":
        return (
            "只能做样本级 smoke 判断，不能做统计结论；当前样本显示平均模拟改善 "
            f"{result.summary.average_simulated_edge:g} 点，可靠性标记为 LOW_SAMPLE。"
        )
    return f"可以做基线判断；当前平均模拟改善 {result.summary.average_simulated_edge:g} 点。"


def write_quant_system_gap_report(path: Path, result: QuantBaselineResult, verification: str) -> None:
    implemented = {
        "Data loader": "implemented for repository fixtures - static option chain loader plus TASK-010 multi-snapshot quote replay loader.",
        "Contract parser": "partial - schema fields are parsed; symbol-level expiry/type parsing remains basic.",
        "Time-value radar": "baseline implemented in TASK-009 from local sample option chain.",
        "Low-liquidity scanner": "implemented for sample open-interest and low-volume ranking.",
        "Combination generator": "implemented for adjacent-strike vertical spreads by expiry/type.",
        "Scoring engine": "baseline implemented with expected edge, fill probability, liquidity, risk and second-leg cost.",
        "State-machine simulator": "implemented for static baseline and TASK-010 ordered multi-snapshot replay with repricing, stale quotes, timeout, fill and incomplete-leg states.",
        "Second-leg protection": "implemented for fixture replay as adverse-move measurement plus deterministic protection threshold.",
        "Replay and reporting": "implemented for markdown reports and replay CSV with static and multi-snapshot replay metrics.",
        "Dashboard/app": "partial - status dashboard exists; quant tables are still report-only.",
    }
    lines = [
        "# Quant System Gap Report",
        "",
        "结论：TASK-010 已在 TASK-009 基线上补齐仓库本地多快照报价 replay fixture 和 loader。当前系统可以用本地 fixture 验证有序快照、陈旧报价、第一腿超时、被动成交概率、补腿不利变动、不完整腿和确定性改价/超时行为；但它仍然不能形成真实收益或真实成交统计结论。",
        "",
        "## Safety Mode",
        "",
        "- Current mode: `PHASE_1_SIMULATION_ONLY`.",
        "- Data scope: repository-local CSV sample and generated replay CSV only.",
        "- Blocked: real trading account connection, real order placement, order cancellation, fund transfer, broker permission change, original-data deletion, secret exposure, dangerous sandbox.",
        "",
        "## Current Coverage",
        "",
        "| Target module | Current coverage |",
        "|---|---|",
    ]
    lines.extend(f"| {module} | {status} |" for module, status in implemented.items())
    lines.extend(
        [
            "",
            "## Data Coverage",
            "",
            f"- Input option sample: `{_rel(SAMPLE_CONTRACTS)}`.",
            f"- Raw contracts: {len(result.raw_contracts)}.",
            f"- Contracts after scan gates: {len(result.scanned_contracts)}.",
            f"- Low-liquidity contracts with open interest: {result.low_liquidity_count}.",
            f"- Vertical spread candidates: {len(result.candidates)}.",
            f"- Multi-snapshot replay fixture: `{_rel(QUOTE_REPLAY_FIXTURE)}`.",
            f"- Quote replay snapshots: {len(result.quote_snapshots)}.",
            f"- Quote replay spread candidates: {len(result.quote_replay_results)}.",
            f"- Replay first-leg fills: {sum(1 for item in result.quote_replay_results if item.first_leg_filled)}.",
            f"- Replay incomplete legs: {sum(1 for item in result.quote_replay_results if item.incomplete_leg)}.",
            f"- Replay stale quote observations: {sum(item.stale_quote_count for item in result.quote_replay_results)}.",
            f"- Replay CSV: `{_rel(result.replay_csv)}`.",
            "- Missing data: real tick series, full order book depth, transaction logs, margin schedule, fee schedule by venue, and statistically meaningful historical samples.",
            "",
            "## Can It Answer The Key Question?",
            "",
            can_answer_key_question(result),
            "",
            "Key question: Does passive first-leg plus active second-leg simulation improve combo net price versus immediate baseline after costs?",
            "",
            f"- Current average simulated improvement: {result.summary.average_simulated_edge:g}.",
            f"- Accepted simulated spreads: {result.summary.accepted_candidates}.",
            f"- Rejected simulated spreads: {result.summary.rejected_candidates}.",
            f"- Worst simulated second-leg slippage: {result.summary.worst_simulated_slippage:g}.",
            f"- Reliability: `{result.summary.reliability}`.",
            f"- Risk flags: `{_flags(result.summary.risk_flags)}`.",
            "",
            "## Remaining Gaps",
            "",
            "- Replace the TASK-010 fixture with larger repository-local historical samples once safe, non-account data is available.",
            "- Add option-chain metadata and robust symbol parser for domestic silver option naming variants.",
            "- Add成交回报 fixture so passive-fill and incomplete-leg rates can be validated against fills, not only quote-state assumptions.",
            "- Add parameter sensitivity over fill threshold, maximum adverse move, timeout, and second-leg slippage.",
            "- Add dashboard tables for time-value anomalies, spread ranking, and replay summary.",
            "",
            "## Verification",
            "",
            verification,
            "",
            "## Next Three Safe Codex Tasks",
            "",
            "1. TASK-011: Add parameter sensitivity report for passive fill threshold, timeout, second-leg max adverse move, fee and slippage assumptions.",
            "2. TASK-012: Extend visible dashboard/report layer with time-value anomaly table, spread ranking table, and replay summary link.",
            "3. TASK-013: Add safe repository-local fill-event fixture to validate passive-fill and incomplete-leg assumptions without connecting any broker account.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_backtest_baseline_report(path: Path, result: QuantBaselineResult, verification: str) -> None:
    incomplete_rate = (
        sum(1 for item in result.scored_spreads if item.incomplete_leg) / len(result.scored_spreads)
        if result.scored_spreads
        else 0.0
    )
    replay_incomplete_rate = (
        sum(1 for item in result.quote_replay_results if item.incomplete_leg)
        / len(result.quote_replay_results)
        if result.quote_replay_results
        else 0.0
    )
    replay_timeouts = sum(1 for item in result.quote_replay_results if item.timed_out)
    replay_fills = sum(1 for item in result.quote_replay_results if item.first_leg_filled)
    replay_stale_quotes = sum(item.stale_quote_count for item in result.quote_replay_results)
    lines = [
        "# Backtest Baseline Report",
        "",
        "结论：本次回测基线已跑通“期权链扫描 -> 时间价值雷达 -> 垂直价差生成 -> 评分 -> 第一腿被动成交模拟 -> 第二腿主动补腿模拟 -> 多快照 replay 报告”。当前结果只适合作为 pipeline 验证，不代表真实收益能力。",
        "",
        "## Reproducible Configuration",
        "",
        f"- Contract universe: `{_rel(SAMPLE_CONTRACTS)}`.",
        f"- Multi-snapshot quote fixture: `{_rel(QUOTE_REPLAY_FIXTURE)}`.",
        f"- Scan gate: `volume >= {DEFAULT_MIN_VOLUME}`, `spread_pct <= {DEFAULT_MAX_SPREAD_PCT:.0%}`.",
        "- Entry rule: adjacent-strike vertical spreads by underlying, expiry, and option type.",
        "- First-leg rule: less liquid leg is quoted passively inside its bid-ask spread.",
        "- Replay rule: consume ordered local quote snapshots, skip stale first-leg quotes, reprice deterministic passive limits, timeout after 60 seconds, and mark incomplete legs.",
        "- Second-leg rule: after simulated first-leg fill, the other leg is completed immediately with deterministic active hedge slippage and replay adverse-move protection.",
        "- Exit rule: no live exit; this baseline evaluates entry quality and leg-completion risk only.",
        "- Fee assumption: 0.2 option points per leg.",
        "- Margin/risk assumption: max loss is capped by vertical width for acceptable debit spreads; candidates breaching width are rejected.",
        "- Data source: local fixture/sample only; no broker, account, market feed, paid API, credential, or external execution system access.",
        "",
        "## Result Table",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Raw contracts | {len(result.raw_contracts)} |",
        f"| Contracts after scan | {len(result.scanned_contracts)} |",
        f"| Vertical spread candidates | {len(result.candidates)} |",
        f"| Accepted simulated spreads | {result.summary.accepted_candidates} |",
        f"| Rejected simulated spreads | {result.summary.rejected_candidates} |",
        f"| Trade count | {result.summary.trade_count} |",
        f"| Win rate | {result.summary.win_rate:.2%} |",
        f"| Average net improvement | {result.summary.average_simulated_edge:g} |",
        f"| Worst simulated second-leg slippage | {result.summary.worst_simulated_slippage:g} |",
        f"| Max drawdown | {result.summary.max_drawdown:g} |",
        f"| Incomplete-leg rate | {incomplete_rate:.2%} |",
        f"| Quote replay snapshots | {len(result.quote_snapshots)} |",
        f"| Quote replay candidates | {len(result.quote_replay_results)} |",
        f"| Replay first-leg fills | {replay_fills} |",
        f"| Replay first-leg timeouts | {replay_timeouts} |",
        f"| Replay incomplete-leg rate | {replay_incomplete_rate:.2%} |",
        f"| Replay stale quote observations | {replay_stale_quotes} |",
        f"| Reliability | {result.summary.reliability} |",
        "",
        "## Top Scored Spreads",
        "",
        "| Rank | Long | Short | Type | Expiry | Strikes | Fill Prob | Sim Edge | Expected Edge | Second-leg Cost | Max Adverse Move | Score | State Path | Flags |",
        "|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for rank, item in enumerate(result.scored_spreads[:8], start=1):
        candidate = item.candidate
        lines.append(
            f"| {rank} | {candidate.long_symbol} | {candidate.short_symbol} | {candidate.option_type} | "
            f"{candidate.expiry} | {candidate.lower_strike:g}-{candidate.upper_strike:g} | "
            f"{item.fill_probability:.2%} | {item.simulation.simulated_edge:g} | {item.expected_edge:g} | "
            f"{item.second_leg_cost_estimate:g} | {item.max_adverse_move:g} | {item.total_score:g} | "
            f"{' > '.join(item.state_path)} | {_flags(item.simulation.risk_flags)} |"
        )

    lines.extend(
        [
            "",
            "## Time-Value Radar",
            "",
            "| Symbol | Type | Expiry | Strike | Inferred Underlying | Intrinsic | Mid Time Value | Spread % | Parity Dev | Flags |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in result.time_value_rows:
        parity = "" if row.parity_deviation is None else f"{row.parity_deviation:g}"
        lines.append(
            f"| {row.symbol} | {row.option_type} | {row.expiry} | {row.strike:g} | "
            f"{row.inferred_underlying:g} | {row.intrinsic:g} | {row.mid_time_value:g} | "
            f"{row.spread_pct:.2%} | {parity} | {_flags(row.flags)} |"
        )

    lines.extend(
        [
            "",
            "## Replay Summary",
            "",
            f"- Replay CSV: `{_rel(result.replay_csv)}`.",
            f"- State paths used: accepted candidates use `{' > '.join(STATE_DONE)}`; incomplete/rejected candidates use `{' > '.join(STATE_FAILED)}`.",
            "- TASK-010 replay state paths include `STALE_QUOTE`, `REPRICED`, `FIRST_LEG_TIMEOUT`, `INCOMPLETE_LEG`, `SECOND_LEG_PROTECTION`, and `DONE` when triggered by ordered snapshots.",
            f"- Maximum adverse move observed: {max((item.max_adverse_move for item in result.scored_spreads), default=0.0):g}.",
            f"- Maximum replay second-leg adverse move observed: {max((item.second_leg_adverse_move for item in result.quote_replay_results), default=0.0):g}.",
            "",
            "## Multi-Snapshot Quote Replay",
            "",
            "| Candidate | First Leg | Hedge Leg | Snapshots | Fill Prob | Timeout Sec | Elapsed Sec | Stale Quotes | Reprices | Filled | Timed Out | Incomplete | Second-Leg Adverse | State Path | Flags |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for replay in result.quote_replay_results:
        lines.append(
            f"| {replay.candidate.long_symbol}/{replay.candidate.short_symbol} | "
            f"{replay.first_leg_action} {replay.first_leg_symbol} | "
            f"{replay.hedge_action} {replay.hedge_leg_symbol} | "
            f"{replay.snapshot_count} | {replay.passive_fill_probability:.2%} | "
            f"{replay.first_leg_timeout_seconds} | {replay.elapsed_seconds} | "
            f"{replay.stale_quote_count} | {replay.reprice_count} | "
            f"{replay.first_leg_filled} | {replay.timed_out} | {replay.incomplete_leg} | "
            f"{replay.second_leg_adverse_move:g} | {' > '.join(replay.state_path)} | "
            f"{_flags(replay.risk_flags)} |"
        )

    lines.extend(
        [
            "",
            "## Risk Summary",
            "",
        ]
    )
    if result.risk_issues:
        lines.extend(f"- {issue}" for issue in result.risk_issues)
    else:
        lines.append("- None.")
    lines.extend(
        [
            f"- Sample-size warning: `{result.summary.reliability}`.",
            f"- Risk flags: `{_flags(result.summary.risk_flags)}`.",
            "",
            "## Verification",
            "",
            verification,
            "",
            "## Safety Boundary",
            "",
            "- Real trading account connection: blocked and not used.",
            "- Real order placement/cancellation: blocked and not used.",
            "- Fund transfer: blocked and not used.",
            "- Original/raw data deletion: blocked and not used.",
            "- Secrets/API keys/passwords/tokens: not used.",
            "- Dangerous sandbox: not used.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_quant_baseline(verification: str = "- Verification not yet run for this report generation.") -> QuantBaselineResult:
    raw_contracts = load_contracts(SAMPLE_CONTRACTS)
    scanned_contracts = scan_contracts(raw_contracts, DEFAULT_MIN_VOLUME, DEFAULT_MAX_SPREAD_PCT)
    low_liquidity = scan_low_liquidity_contracts(raw_contracts)
    candidates = calculate_vertical_spreads(scanned_contracts)
    simulations, summary = run_first_complete_simulation(scanned_contracts, candidates, TRADING_MODE)
    risk_issues = check_research_risk(scanned_contracts, candidates, TRADING_MODE, simulations, summary)
    backtest = run_simple_backtest(candidates)
    time_value_rows = build_time_value_radar(raw_contracts)
    scored_spreads = score_spreads(candidates, simulations)
    quote_snapshots = load_quote_snapshots(QUOTE_REPLAY_FIXTURE)
    quote_replay_results = replay_vertical_spreads(candidates, quote_snapshots)
    write_replay_csv(QUANT_BASELINE_REPLAY_CSV, scored_spreads, quote_replay_results)
    result = QuantBaselineResult(
        raw_contracts=raw_contracts,
        scanned_contracts=scanned_contracts,
        low_liquidity_count=len(low_liquidity),
        time_value_rows=time_value_rows,
        candidates=candidates,
        simulations=simulations,
        scored_spreads=scored_spreads,
        quote_snapshots=quote_snapshots,
        quote_replay_results=quote_replay_results,
        summary=summary,
        backtest=backtest,
        risk_issues=risk_issues,
        replay_csv=QUANT_BASELINE_REPLAY_CSV,
    )
    write_quant_system_gap_report(QUANT_SYSTEM_GAP_REPORT, result, verification)
    write_backtest_baseline_report(BACKTEST_BASELINE_REPORT, result, verification)
    return result
