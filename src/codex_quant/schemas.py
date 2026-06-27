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


@dataclass(frozen=True)
class SpreadSimulation:
    candidate: SpreadCandidate
    first_leg_symbol: str
    first_leg_action: str
    passive_limit_price: float
    passive_fill_probability: float
    passive_edge: float
    hedge_leg_symbol: str
    hedge_action: str
    hedge_slippage: float
    simulated_net_debit: float
    simulated_edge: float
    max_loss: float
    accepted: bool
    rejection_reason: str
    risk_flags: tuple[str, ...]


@dataclass(frozen=True)
class SimulationSummary:
    contracts_scanned: int
    spread_candidates: int
    rejected_candidates: int
    accepted_candidates: int
    average_simulated_edge: float
    worst_simulated_slippage: float
    trade_count: int
    win_rate: float
    max_drawdown: float
    reliability: str
    risk_flags: tuple[str, ...]
