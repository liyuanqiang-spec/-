from pathlib import Path

from .schemas import OptionContract, SpreadCandidate


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
