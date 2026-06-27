from .schemas import OptionContract, SimulationSummary, SpreadCandidate, SpreadSimulation


ALLOWED_SIMULATION_MODES = {"SIMULATION_ONLY", "PHASE_1_SIMULATION_ONLY"}


def check_research_risk(
    contracts: list[OptionContract],
    candidates: list[SpreadCandidate],
    trading_mode: str,
    simulations: list[SpreadSimulation] | None = None,
    summary: SimulationSummary | None = None,
) -> list[str]:
    issues: list[str] = []
    if trading_mode not in ALLOWED_SIMULATION_MODES:
        issues.append("BLOCKED: trading mode is not simulation-only")
    if not contracts:
        issues.append("NO_CONTRACTS: no contracts passed liquidity scan")
    if not candidates:
        issues.append("NO_SPREADS: no spread candidates were created")
    if any(candidate.net_debit <= 0 for candidate in candidates):
        issues.append("CHECK_PRICING: non-positive net debit found")
    if len(candidates) < 20:
        issues.append("LOW_SAMPLE: candidate count is below 20")
    if simulations is not None and summary is not None:
        if summary.rejected_candidates:
            issues.append(f"REJECTED_CANDIDATES: {summary.rejected_candidates} candidate(s) failed simulation gates")
        if summary.worst_simulated_slippage > 4.0:
            issues.append("WIDE_HEDGE_SLIPPAGE: worst simulated hedge slippage exceeds 4 points")
        if summary.trade_count < 5:
            issues.append("LOW_TRADE_COUNT: fewer than 5 simulated accepted spreads")
        if any("MISSING_LEG_CONTRACT" in simulation.risk_flags for simulation in simulations):
            issues.append("MISSING_LEG_CONTRACT: candidate references a missing contract")
    return issues
