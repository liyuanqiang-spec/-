from collections import defaultdict

from .schemas import OptionContract, SpreadCandidate


def calculate_vertical_spreads(contracts: list[OptionContract]) -> list[SpreadCandidate]:
    groups: dict[tuple[str, str, str], list[OptionContract]] = defaultdict(list)
    for contract in contracts:
        groups[(contract.underlying, contract.expiry, contract.option_type)].append(contract)

    candidates: list[SpreadCandidate] = []
    for (underlying, expiry, option_type), group in groups.items():
        ordered = sorted(group, key=lambda item: item.strike)
        for lower, upper in zip(ordered, ordered[1:]):
            if option_type == "C":
                net_debit = lower.ask - upper.bid
                long_symbol, short_symbol = lower.symbol, upper.symbol
            else:
                net_debit = upper.ask - lower.bid
                long_symbol, short_symbol = upper.symbol, lower.symbol
            width = abs(upper.strike - lower.strike)
            liquidity_score = (lower.volume + upper.volume) / max(lower.spread_pct + upper.spread_pct, 0.01)
            candidates.append(
                SpreadCandidate(
                    long_symbol=long_symbol,
                    short_symbol=short_symbol,
                    underlying=underlying,
                    expiry=expiry,
                    option_type=option_type,
                    lower_strike=lower.strike,
                    upper_strike=upper.strike,
                    net_debit=round(net_debit, 4),
                    width=width,
                    liquidity_score=round(liquidity_score, 2),
                )
            )
    return sorted(candidates, key=lambda item: item.liquidity_score, reverse=True)
