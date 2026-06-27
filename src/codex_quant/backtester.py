from .schemas import OptionContract, SimulationSummary, SpreadCandidate, SpreadSimulation


ALLOWED_SIMULATION_MODES = {"SIMULATION_ONLY", "PHASE_1_SIMULATION_ONLY"}
PASSIVE_FILL_PROBABILITY_FLOOR = 0.35
MAX_HEDGE_SLIPPAGE_POINTS = 4.0
FEE_PER_LEG_POINTS = 0.2


def run_simple_backtest(candidates: list[SpreadCandidate]) -> dict[str, float | int | str]:
    if not candidates:
        return {
            "trade_count": 0,
            "estimated_edge": 0.0,
            "max_loss_per_spread": 0.0,
            "reliability": "NO_DATA",
        }

    best = candidates[0]
    max_loss = max(best.net_debit, 0)
    estimated_edge = max(best.width * 0.1 - best.net_debit * 0.05, 0)
    reliability = "LOW_SAMPLE" if len(candidates) < 20 else "OK"
    return {
        "trade_count": len(candidates),
        "estimated_edge": round(estimated_edge, 4),
        "max_loss_per_spread": round(max_loss, 4),
        "reliability": reliability,
    }


def _leg_action(candidate: SpreadCandidate, symbol: str) -> str:
    return "BUY" if symbol == candidate.long_symbol else "SELL"


def _passive_leg_score(contract: OptionContract) -> float:
    volume_risk = 1.0 - min(contract.volume / 120, 1.0)
    spread_risk = min(contract.spread_pct / 0.25, 1.0)
    return volume_risk + spread_risk


def _passive_fill_probability(contract: OptionContract) -> float:
    volume_component = min(contract.volume / 120, 1.0) * 0.45
    open_interest_component = min(contract.open_interest / 800, 1.0) * 0.25
    tightness_component = max(0.0, 1.0 - min(contract.spread_pct / 0.25, 1.0)) * 0.30
    return round(max(0.05, min(volume_component + open_interest_component + tightness_component, 0.95)), 4)


def _passive_limit_price(contract: OptionContract, action: str) -> float:
    if action == "BUY":
        return round(contract.bid + contract.spread * 0.25, 4)
    return round(contract.ask - contract.spread * 0.25, 4)


def _passive_edge(contract: OptionContract, passive_price: float, action: str) -> float:
    edge = contract.mid - passive_price if action == "BUY" else passive_price - contract.mid
    return round(max(edge, 0.0), 4)


def _hedge_slippage(contract: OptionContract) -> float:
    low_volume_component = max(0, 80 - contract.volume) / 200
    spread_component = min(contract.spread_pct / 0.25, 1.0) * 0.20
    return round(contract.spread * (0.15 + low_volume_component + spread_component), 4)


def _signed_cost(action: str, price: float) -> float:
    return price if action == "BUY" else -price


def _drawdown(edges: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for edge in edges:
        equity += edge
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return round(max_drawdown, 4)


def simulate_spread_candidate(
    candidate: SpreadCandidate,
    contracts_by_symbol: dict[str, OptionContract],
) -> SpreadSimulation:
    long_contract = contracts_by_symbol[candidate.long_symbol]
    short_contract = contracts_by_symbol[candidate.short_symbol]
    first_contract, hedge_contract = sorted(
        [long_contract, short_contract],
        key=_passive_leg_score,
        reverse=True,
    )
    first_action = _leg_action(candidate, first_contract.symbol)
    hedge_action = _leg_action(candidate, hedge_contract.symbol)
    passive_price = _passive_limit_price(first_contract, first_action)
    passive_edge = _passive_edge(first_contract, passive_price, first_action)
    fill_probability = _passive_fill_probability(first_contract)
    hedge_slippage = _hedge_slippage(hedge_contract)

    if hedge_action == "BUY":
        hedge_price = hedge_contract.ask + hedge_slippage
    else:
        hedge_price = hedge_contract.bid - hedge_slippage

    simulated_net_debit = (
        _signed_cost(first_action, passive_price)
        + _signed_cost(hedge_action, hedge_price)
        + FEE_PER_LEG_POINTS * 2
    )
    baseline_net_debit = candidate.net_debit + FEE_PER_LEG_POINTS * 2
    simulated_edge = baseline_net_debit - simulated_net_debit
    max_loss = max(simulated_net_debit, 0.0)

    risk_flags: list[str] = []
    if candidate.net_debit <= 0:
        risk_flags.append("NON_POSITIVE_NET_DEBIT")
    if fill_probability < PASSIVE_FILL_PROBABILITY_FLOOR:
        risk_flags.append("LOW_PASSIVE_FILL")
    if hedge_slippage > MAX_HEDGE_SLIPPAGE_POINTS:
        risk_flags.append("HEDGE_SLIPPAGE_WIDE")
    if first_contract.spread_pct > 0.15 or hedge_contract.spread_pct > 0.15:
        risk_flags.append("WIDE_LEG_SPREAD")
    if simulated_edge <= 0:
        risk_flags.append("NEGATIVE_SIMULATED_EDGE")
    if max_loss > candidate.width:
        risk_flags.append("MAX_LOSS_EXCEEDS_WIDTH")

    blocking_flags = {
        "NON_POSITIVE_NET_DEBIT",
        "LOW_PASSIVE_FILL",
        "HEDGE_SLIPPAGE_WIDE",
        "MAX_LOSS_EXCEEDS_WIDTH",
    }
    accepted = not any(flag in blocking_flags for flag in risk_flags)
    rejection_reason = "; ".join(flag for flag in risk_flags if flag in blocking_flags)

    return SpreadSimulation(
        candidate=candidate,
        first_leg_symbol=first_contract.symbol,
        first_leg_action=first_action,
        passive_limit_price=round(passive_price, 4),
        passive_fill_probability=fill_probability,
        passive_edge=round(passive_edge, 4),
        hedge_leg_symbol=hedge_contract.symbol,
        hedge_action=hedge_action,
        hedge_slippage=round(hedge_slippage, 4),
        simulated_net_debit=round(simulated_net_debit, 4),
        simulated_edge=round(simulated_edge, 4),
        max_loss=round(max_loss, 4),
        accepted=accepted,
        rejection_reason=rejection_reason,
        risk_flags=tuple(risk_flags),
    )


def run_first_complete_simulation(
    contracts: list[OptionContract],
    candidates: list[SpreadCandidate],
    trading_mode: str,
) -> tuple[list[SpreadSimulation], SimulationSummary]:
    if trading_mode not in ALLOWED_SIMULATION_MODES:
        summary = SimulationSummary(
            contracts_scanned=len(contracts),
            spread_candidates=len(candidates),
            rejected_candidates=len(candidates),
            accepted_candidates=0,
            average_simulated_edge=0.0,
            worst_simulated_slippage=0.0,
            trade_count=0,
            win_rate=0.0,
            max_drawdown=0.0,
            reliability="BLOCKED_MODE",
            risk_flags=("BLOCKED_TRADING_MODE",),
        )
        return [], summary

    contracts_by_symbol = {contract.symbol: contract for contract in contracts}
    simulations = [
        simulate_spread_candidate(candidate, contracts_by_symbol)
        for candidate in candidates
        if candidate.long_symbol in contracts_by_symbol and candidate.short_symbol in contracts_by_symbol
    ]
    accepted = [simulation for simulation in simulations if simulation.accepted]
    edge_basis = accepted or simulations
    edges = [simulation.simulated_edge for simulation in edge_basis]
    average_edge = round(sum(edges) / len(edges), 4) if edges else 0.0
    worst_slippage = round(max((simulation.hedge_slippage for simulation in simulations), default=0.0), 4)
    win_rate = round(
        sum(1 for simulation in accepted if simulation.simulated_edge > 0) / len(accepted),
        4,
    ) if accepted else 0.0

    risk_flags = {flag for simulation in simulations for flag in simulation.risk_flags}
    if len(candidates) < 20:
        risk_flags.add("LOW_SAMPLE")
    if not contracts:
        risk_flags.add("NO_CONTRACTS")
    if not candidates:
        risk_flags.add("NO_SPREADS")
    if len(simulations) != len(candidates):
        risk_flags.add("MISSING_LEG_CONTRACT")

    reliability = "NO_DATA"
    if candidates:
        reliability = "LOW_SAMPLE" if len(candidates) < 20 else "OK"

    summary = SimulationSummary(
        contracts_scanned=len(contracts),
        spread_candidates=len(candidates),
        rejected_candidates=len(candidates) - len(accepted),
        accepted_candidates=len(accepted),
        average_simulated_edge=average_edge,
        worst_simulated_slippage=worst_slippage,
        trade_count=len(accepted),
        win_rate=win_rate,
        max_drawdown=_drawdown([simulation.simulated_edge for simulation in accepted]),
        reliability=reliability,
        risk_flags=tuple(sorted(risk_flags)),
    )
    return simulations, summary
