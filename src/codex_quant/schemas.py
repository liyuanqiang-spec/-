from dataclasses import dataclass


@dataclass(frozen=True)
class OptionContract:
    symbol: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    bid: float
    ask: float
    volume: int
    open_interest: int

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def spread_pct(self) -> float:
        return self.spread / self.mid if self.mid > 0 else float("inf")


@dataclass(frozen=True)
class SpreadCandidate:
    long_symbol: str
    short_symbol: str
    underlying: str
    expiry: str
    option_type: str
    lower_strike: float
    upper_strike: float
    net_debit: float
    width: float
    liquidity_score: float
