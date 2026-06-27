import json
from dataclasses import asdict
from pathlib import Path

from .schemas import OptionContract, SimulationSummary, SpreadCandidate, SpreadSimulation


def write_report(
    path: Path,
    contracts: list[OptionContract],
    candidates: list[SpreadCandidate],
    backtest: dict[str, float | int | str],
    risk_issues: list[str],
) -> None:
    lines = [
        "# Codex Quant Minimal Report",
        "",
        "结论：当前系统处于 `SIMULATION_ONLY`，本报告只基于样例数据，不代表真实交易建议。",
        "",
        "## Summary",
        "",
        f"- Contracts after scan: {len(contracts)}",
        f"- Spread candidates: {len(candidates)}",
        f"- Backtest reliability: {backtest['reliability']}",
        f"- Estimated edge: {backtest['estimated_edge']}",
        f"- Max loss per spread: {backtest['max_loss_per_spread']}",
        "",
        "## Top Candidates",
        "",
        "| Long | Short | Type | Expiry | Strikes | Net Debit | Liquidity Score |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for candidate in candidates[:5]:
        lines.append(
            "| "
            f"{candidate.long_symbol} | {candidate.short_symbol} | {candidate.option_type} | "
            f"{candidate.expiry} | {candidate.lower_strike:g}-{candidate.upper_strike:g} | "
            f"{candidate.net_debit:g} | {candidate.liquidity_score:g} |"
        )

    lines.extend(["", "## Risk Issues", ""])
    if risk_issues:
        lines.extend(f"- {issue}" for issue in risk_issues)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Real trading: blocked",
            "- Broker orders: blocked",
            "- Fund transfer: blocked",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _flags_text(flags: tuple[str, ...] | list[str]) -> str:
    return ", ".join(flags) if flags else "None"


def write_simulation_summary_json(path: Path, summary: SimulationSummary, risk_issues: list[str]) -> None:
    payload = asdict(summary)
    payload["risk_flags"] = list(summary.risk_flags)
    payload["risk_issues"] = risk_issues
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_first_complete_simulation_report(
    path: Path,
    raw_contracts: list[OptionContract],
    scanned_contracts: list[OptionContract],
    candidates: list[SpreadCandidate],
    simulations: list[SpreadSimulation],
    summary: SimulationSummary,
    risk_issues: list[str],
    command: str,
) -> None:
    scanned_symbols = {contract.symbol for contract in scanned_contracts}
    excluded_contracts = [contract for contract in raw_contracts if contract.symbol not in scanned_symbols]
    accepted = [simulation for simulation in simulations if simulation.accepted]
    rejected = [simulation for simulation in simulations if not simulation.accepted]

    lines = [
        "# TASK-007 First Complete Simulation Report",
        "",
        "结论：第一版完整模拟链路已跑通。它只读取本地样例白银期权数据，生成垂直价差候选，估算被动第一腿成交机会，模拟第二腿补腿滑点，执行风控检查，并写出本报告。全程未连接真实交易账户，未下单，未撤单，未转账。",
        "",
        "## Run Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## Dashboard Entry",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Contracts scanned | {summary.contracts_scanned} |",
        f"| Vertical spread candidates | {summary.spread_candidates} |",
        f"| Rejected candidates | {summary.rejected_candidates} |",
        f"| Accepted simulated spreads | {summary.accepted_candidates} |",
        f"| Average simulated edge | {summary.average_simulated_edge:g} |",
        f"| Worst simulated slippage | {summary.worst_simulated_slippage:g} |",
        f"| Trade count | {summary.trade_count} |",
        f"| Win rate | {summary.win_rate:.2%} |",
        f"| Max drawdown | {summary.max_drawdown:g} |",
        f"| Reliability | {summary.reliability} |",
        f"| Risk flags | {_flags_text(summary.risk_flags)} |",
        "",
        "## Reproducible Backtest Configuration",
        "",
        f"- Contract universe: `{len(raw_contracts)}` local sample silver option contracts from `data/contracts/sample_options.csv`.",
        "- Entry rule: build adjacent-strike vertical spreads by underlying, expiry, and option type; first leg is selected as the less liquid leg and quoted passively inside the spread.",
        "- Second-leg rule: once the passive first leg is assumed filled, hedge the other leg immediately with deterministic slippage based on spread width and volume.",
        "- Exit rule: no live exit order is simulated; this first version evaluates entry quality and maximum entry risk only.",
        "- Fee assumption: `0.2` option points per leg.",
        "- Slippage assumption: second-leg slippage is a deterministic function of bid-ask spread, spread percentage, and low-volume penalty.",
        "- Data source: local sample CSV only; no market connection, account query, broker API, credentials, or external paid API call.",
        "",
        "## Candidate Simulation Table",
        "",
        "| Rank | Long | Short | Type | Expiry | Strikes | Net Debit | First Leg | Passive Fill Prob | Passive Edge | Hedge Leg | Hedge Slippage | Sim Edge | Accepted | Risk Flags |",
        "|---:|---|---|---:|---|---:|---:|---|---:|---:|---|---:|---:|---:|---|",
    ]

    for rank, simulation in enumerate(simulations, start=1):
        candidate = simulation.candidate
        lines.append(
            f"| {rank} | {candidate.long_symbol} | {candidate.short_symbol} | {candidate.option_type} | "
            f"{candidate.expiry} | {candidate.lower_strike:g}-{candidate.upper_strike:g} | "
            f"{candidate.net_debit:g} | {simulation.first_leg_action} {simulation.first_leg_symbol} @ {simulation.passive_limit_price:g} | "
            f"{simulation.passive_fill_probability:.2%} | {simulation.passive_edge:g} | "
            f"{simulation.hedge_action} {simulation.hedge_leg_symbol} | {simulation.hedge_slippage:g} | "
            f"{simulation.simulated_edge:g} | {'yes' if simulation.accepted else 'no'} | "
            f"{_flags_text(simulation.risk_flags)} |"
        )

    lines.extend(
        [
            "",
            "## Accepted Candidates",
            "",
        ]
    )
    if accepted:
        lines.extend(
            f"- {simulation.candidate.long_symbol}/{simulation.candidate.short_symbol}: simulated edge {simulation.simulated_edge:g}, fill probability {simulation.passive_fill_probability:.2%}."
            for simulation in accepted
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Rejected Candidates", ""])
    if rejected:
        lines.extend(
            f"- {simulation.candidate.long_symbol}/{simulation.candidate.short_symbol}: {simulation.rejection_reason or _flags_text(simulation.risk_flags)}."
            for simulation in rejected
        )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Contract Scan Rejections",
            "",
            "| Symbol | Volume | Open Interest | Spread % | Reason |",
            "|---|---:|---:|---:|---|",
        ]
    )
    if excluded_contracts:
        for contract in excluded_contracts:
            reason = []
            if contract.bid <= 0:
                reason.append("bid <= 0")
            if contract.ask <= contract.bid:
                reason.append("ask <= bid")
            if contract.volume < 30:
                reason.append("volume below minimum")
            if contract.spread_pct > 0.25:
                reason.append("spread percentage above maximum")
            lines.append(
                f"| {contract.symbol} | {contract.volume} | {contract.open_interest} | "
                f"{contract.spread_pct:.2%} | {', '.join(reason) or 'passed scan'} |"
            )
    else:
        lines.append("| None |  |  |  | All sample contracts passed the scan gate |")

    lines.extend(
        [
            "",
            "## Risk Checks",
            "",
        ]
    )
    if risk_issues:
        lines.extend(f"- {issue}" for issue in risk_issues)
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- Phase: `PHASE_1_SIMULATION_ONLY`.",
            "- Real trading account connection: blocked and not used.",
            "- Real order placement/cancellation: blocked and not used.",
            "- Fund transfer: blocked and not used.",
            "- Original/raw data deletion: blocked and not used.",
            "- Secrets, passwords, tokens, and API keys: not read or exposed.",
            "- `danger-full-access`: not used.",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
