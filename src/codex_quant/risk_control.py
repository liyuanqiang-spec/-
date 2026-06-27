from .schemas import OptionContract, SpreadCandidate


def check_research_risk(
    contracts: list[OptionContract],
    candidates: list[SpreadCandidate],
    trading_mode: str,
) -> list[str]:
    issues: list[str] = []
    if trading_mode != "SIMULATION_ONLY":
        issues.append("BLOCKED: trading mode is not SIMULATION_ONLY")
    if not contracts:
        issues.append("NO_CONTRACTS: no contracts passed liquidity scan")
    if not candidates:
        issues.append("NO_SPREADS: no spread candidates were created")
    if any(candidate.net_debit <= 0 for candidate in candidates):
        issues.append("CHECK_PRICING: non-positive net debit found")
    if len(candidates) < 20:
        issues.append("LOW_SAMPLE: candidate count is below 20")
    return issues
