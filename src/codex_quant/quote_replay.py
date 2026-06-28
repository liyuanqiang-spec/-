from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .schemas import SpreadCandidate


@dataclass(frozen=True)
class QuoteSnapshot:
    snapshot_id: int
    timestamp: datetime
    timestamp_text: str
    symbol: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    bid_depth: int
    ask_depth: int
    quote_age_seconds: float
    freshness_status: str
    is_stale: bool
    source_note: str

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def spread_pct(self) -> float:
        return self.spread / self.mid if self.mid > 0 else float("inf")

    @property
    def visible_size(self) -> int:
        return self.bid_size + self.ask_size

    @property
    def visible_depth(self) -> int:
        return self.bid_depth + self.ask_depth


@dataclass(frozen=True)
class QuoteReplayResult:
    candidate: SpreadCandidate
    first_leg_symbol: str
    first_leg_action: str
    hedge_leg_symbol: str
    hedge_action: str
    snapshot_count: int
    first_timestamp: str
    final_timestamp: str
    fill_timestamp: str
    state_path: tuple[str, ...]
    first_leg_timeout_seconds: int
    elapsed_seconds: int
    first_leg_filled: bool
    timed_out: bool
    incomplete_leg: bool
    stale_quote_count: int
    reprice_count: int
    passive_limit_price: float
    passive_fill_probability: float
    baseline_hedge_price: float
    hedge_price: float
    second_leg_adverse_move: float
    risk_flags: tuple[str, ...]


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "stale"}


def load_quote_snapshots(path: Path) -> list[QuoteSnapshot]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f)
        snapshots = [
            QuoteSnapshot(
                snapshot_id=int(row["snapshot_id"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                timestamp_text=row["timestamp"],
                symbol=row["symbol"],
                underlying=row["underlying"],
                expiry=row["expiry"],
                strike=float(row["strike"]),
                option_type=row["option_type"].upper(),
                bid=float(row["bid"]),
                ask=float(row["ask"]),
                bid_size=int(row["bid_size"]),
                ask_size=int(row["ask_size"]),
                bid_depth=int(row["bid_depth"]),
                ask_depth=int(row["ask_depth"]),
                quote_age_seconds=float(row["quote_age_seconds"]),
                freshness_status=row["freshness_status"].upper(),
                is_stale=_parse_bool(row["is_stale"]),
                source_note=row.get("source_note", ""),
            )
            for row in rows
        ]
    for snapshot in snapshots:
        if snapshot.bid <= 0 or snapshot.ask <= snapshot.bid:
            raise ValueError(f"invalid quote for {snapshot.symbol} at {snapshot.timestamp_text}")
    return sorted(snapshots, key=lambda item: (item.timestamp, item.snapshot_id, item.symbol))


def estimate_passive_fill_probability(
    quote: QuoteSnapshot,
    stale_after_seconds: int = 30,
) -> float:
    if quote.is_stale or quote.quote_age_seconds > stale_after_seconds:
        return 0.0
    size_component = min(quote.visible_size / 80, 1.0) * 0.25
    depth_component = min(quote.visible_depth / 250, 1.0) * 0.25
    tightness_component = max(0.0, 1.0 - min(quote.spread_pct / 0.20, 1.0)) * 0.30
    freshness_component = max(0.0, 1.0 - min(quote.quote_age_seconds / stale_after_seconds, 1.0)) * 0.20
    return round(size_component + depth_component + tightness_component + freshness_component, 4)


def _candidate_timeline(
    snapshots: list[QuoteSnapshot],
    candidate: SpreadCandidate,
) -> list[tuple[datetime, dict[str, QuoteSnapshot]]]:
    grouped: dict[datetime, dict[str, QuoteSnapshot]] = {}
    for snapshot in snapshots:
        grouped.setdefault(snapshot.timestamp, {})[snapshot.symbol] = snapshot
    symbols = {candidate.long_symbol, candidate.short_symbol}
    return [
        (timestamp, quotes)
        for timestamp, quotes in sorted(grouped.items())
        if symbols.issubset(quotes)
    ]


def _leg_action(candidate: SpreadCandidate, symbol: str) -> str:
    return "BUY" if symbol == candidate.long_symbol else "SELL"


def _liquidity_risk(quote: QuoteSnapshot) -> float:
    visible_size = max(quote.visible_size, 1)
    visible_depth = max(quote.visible_depth, 1)
    return quote.spread_pct * 4 + 1 / visible_size + 1 / visible_depth


def _passive_limit_price(quote: QuoteSnapshot, action: str) -> float:
    if action == "BUY":
        return round(quote.bid + quote.spread * 0.25, 4)
    return round(quote.ask - quote.spread * 0.25, 4)


def _active_hedge_price(quote: QuoteSnapshot, action: str) -> float:
    return quote.ask if action == "BUY" else quote.bid


def _adverse_move(initial_price: float, hedge_price: float, action: str) -> float:
    if action == "BUY":
        return round(max(0.0, hedge_price - initial_price), 4)
    return round(max(0.0, initial_price - hedge_price), 4)


def replay_spread_candidate(
    candidate: SpreadCandidate,
    snapshots: list[QuoteSnapshot],
    first_leg_timeout_seconds: int = 60,
    passive_fill_threshold: float = 0.60,
    max_second_leg_adverse_move_points: float = 3.0,
) -> QuoteReplayResult | None:
    timeline = _candidate_timeline(snapshots, candidate)
    if not timeline:
        return None

    start_time, initial_quotes = timeline[0]
    long_initial = initial_quotes[candidate.long_symbol]
    short_initial = initial_quotes[candidate.short_symbol]
    first_quote = max((long_initial, short_initial), key=_liquidity_risk)
    hedge_symbol = (
        candidate.short_symbol
        if first_quote.symbol == candidate.long_symbol
        else candidate.long_symbol
    )
    first_action = _leg_action(candidate, first_quote.symbol)
    hedge_action = _leg_action(candidate, hedge_symbol)
    hedge_initial = initial_quotes[hedge_symbol]
    baseline_hedge_price = _active_hedge_price(hedge_initial, hedge_action)

    state_path: list[str] = ["IDLE", "FOUND", "PENDING_FIRST_LEG"]
    risk_flags: list[str] = []
    stale_quote_count = 0
    reprice_count = 0
    best_probability = 0.0
    last_limit: float | None = None
    final_timestamp = timeline[-1][1][first_quote.symbol].timestamp_text
    final_elapsed = 0

    for timestamp, quotes in timeline:
        elapsed_seconds = int((timestamp - start_time).total_seconds())
        final_elapsed = elapsed_seconds
        current_first = quotes[first_quote.symbol]
        current_hedge = quotes[hedge_symbol]
        final_timestamp = current_first.timestamp_text

        if elapsed_seconds > first_leg_timeout_seconds:
            if "FIRST_LEG_TIMEOUT" not in state_path:
                state_path.extend(["FIRST_LEG_TIMEOUT", "INCOMPLETE_LEG", "COOLDOWN"])
            risk_flags.extend(["FIRST_LEG_TIMEOUT", "INCOMPLETE_LEG"])
            return QuoteReplayResult(
                candidate=candidate,
                first_leg_symbol=first_quote.symbol,
                first_leg_action=first_action,
                hedge_leg_symbol=hedge_symbol,
                hedge_action=hedge_action,
                snapshot_count=len(timeline),
                first_timestamp=timeline[0][1][first_quote.symbol].timestamp_text,
                final_timestamp=final_timestamp,
                fill_timestamp="",
                state_path=tuple(state_path),
                first_leg_timeout_seconds=first_leg_timeout_seconds,
                elapsed_seconds=elapsed_seconds,
                first_leg_filled=False,
                timed_out=True,
                incomplete_leg=True,
                stale_quote_count=stale_quote_count,
                reprice_count=reprice_count,
                passive_limit_price=round(last_limit or _passive_limit_price(current_first, first_action), 4),
                passive_fill_probability=best_probability,
                baseline_hedge_price=round(baseline_hedge_price, 4),
                hedge_price=0.0,
                second_leg_adverse_move=0.0,
                risk_flags=tuple(dict.fromkeys(risk_flags)),
            )

        if current_first.is_stale or current_hedge.is_stale:
            stale_quote_count += int(current_first.is_stale) + int(current_hedge.is_stale)
            if "STALE_QUOTE" not in state_path:
                state_path.append("STALE_QUOTE")
            if "STALE_QUOTE_SEEN" not in risk_flags:
                risk_flags.append("STALE_QUOTE_SEEN")
            continue

        passive_limit = _passive_limit_price(current_first, first_action)
        if last_limit is not None and passive_limit != last_limit:
            reprice_count += 1
            state_path.append("REPRICED")
        last_limit = passive_limit
        probability = estimate_passive_fill_probability(current_first)
        best_probability = max(best_probability, probability)
        if probability < passive_fill_threshold:
            continue

        hedge_price = _active_hedge_price(current_hedge, hedge_action)
        adverse_move = _adverse_move(baseline_hedge_price, hedge_price, hedge_action)
        state_path.extend(["FIRST_LEG_FILLED", "HEDGING_SECOND_LEG"])
        if adverse_move > max_second_leg_adverse_move_points:
            state_path.extend(["SECOND_LEG_PROTECTION", "INCOMPLETE_LEG", "COOLDOWN"])
            risk_flags.extend(["SECOND_LEG_ADVERSE_MOVE_LIMIT", "INCOMPLETE_LEG"])
            incomplete = True
        else:
            state_path.append("DONE")
            incomplete = False
        return QuoteReplayResult(
            candidate=candidate,
            first_leg_symbol=first_quote.symbol,
            first_leg_action=first_action,
            hedge_leg_symbol=hedge_symbol,
            hedge_action=hedge_action,
            snapshot_count=len(timeline),
            first_timestamp=timeline[0][1][first_quote.symbol].timestamp_text,
            final_timestamp=final_timestamp,
            fill_timestamp=current_first.timestamp_text,
            state_path=tuple(state_path),
            first_leg_timeout_seconds=first_leg_timeout_seconds,
            elapsed_seconds=elapsed_seconds,
            first_leg_filled=True,
            timed_out=False,
            incomplete_leg=incomplete,
            stale_quote_count=stale_quote_count,
            reprice_count=reprice_count,
            passive_limit_price=passive_limit,
            passive_fill_probability=probability,
            baseline_hedge_price=round(baseline_hedge_price, 4),
            hedge_price=round(hedge_price, 4),
            second_leg_adverse_move=adverse_move,
            risk_flags=tuple(dict.fromkeys(risk_flags)),
        )

    state_path.extend(["NO_FILL", "INCOMPLETE_LEG", "COOLDOWN"])
    risk_flags.extend(["NO_PASSIVE_FILL", "INCOMPLETE_LEG"])
    return QuoteReplayResult(
        candidate=candidate,
        first_leg_symbol=first_quote.symbol,
        first_leg_action=first_action,
        hedge_leg_symbol=hedge_symbol,
        hedge_action=hedge_action,
        snapshot_count=len(timeline),
        first_timestamp=timeline[0][1][first_quote.symbol].timestamp_text,
        final_timestamp=final_timestamp,
        fill_timestamp="",
        state_path=tuple(state_path),
        first_leg_timeout_seconds=first_leg_timeout_seconds,
        elapsed_seconds=final_elapsed,
        first_leg_filled=False,
        timed_out=False,
        incomplete_leg=True,
        stale_quote_count=stale_quote_count,
        reprice_count=reprice_count,
        passive_limit_price=round(last_limit or 0.0, 4),
        passive_fill_probability=best_probability,
        baseline_hedge_price=round(baseline_hedge_price, 4),
        hedge_price=0.0,
        second_leg_adverse_move=0.0,
        risk_flags=tuple(dict.fromkeys(risk_flags)),
    )


def replay_vertical_spreads(
    candidates: list[SpreadCandidate],
    snapshots: list[QuoteSnapshot],
    first_leg_timeout_seconds: int = 60,
    passive_fill_threshold: float = 0.60,
    max_second_leg_adverse_move_points: float = 3.0,
) -> list[QuoteReplayResult]:
    results: list[QuoteReplayResult] = []
    for candidate in candidates:
        result = replay_spread_candidate(
            candidate,
            snapshots,
            first_leg_timeout_seconds=first_leg_timeout_seconds,
            passive_fill_threshold=passive_fill_threshold,
            max_second_leg_adverse_move_points=max_second_leg_adverse_move_points,
        )
        if result is not None:
            results.append(result)
    return results
