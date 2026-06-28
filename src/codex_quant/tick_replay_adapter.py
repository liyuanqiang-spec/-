from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .contract_scanner import load_contracts
from .quote_replay import QuoteSnapshot, load_quote_snapshots


REQUIRED_TICK_FIELDS = (
    "datetime",
    "symbol",
    "bid_price1",
    "bid_volume1",
    "ask_price1",
    "ask_volume1",
    "last_price",
    "volume",
    "open_interest",
    "trading_date",
    "source",
)

FIELD_ALIASES = {
    "datetime": ("datetime", "timestamp", "ts", "time"),
    "symbol": ("symbol", "instrument_id", "instrument", "contract", "contract_code"),
    "bid_price1": ("bid_price1", "bid_price_1", "bid1", "bid", "bid_price"),
    "bid_volume1": ("bid_volume1", "bid_volume_1", "bid_size", "bid_vol1", "bid_volume"),
    "ask_price1": ("ask_price1", "ask_price_1", "ask1", "ask", "ask_price"),
    "ask_volume1": ("ask_volume1", "ask_volume_1", "ask_size", "ask_vol1", "ask_volume"),
    "last_price": ("last_price", "last", "price", "latest_price"),
    "volume": ("volume", "cum_volume", "total_volume"),
    "open_interest": ("open_interest", "openinterest", "oi"),
    "trading_date": ("trading_date", "trade_date", "date"),
    "source": ("source", "source_note", "data_source"),
}


@dataclass(frozen=True)
class TickSchemaCheck:
    canonical_field: str
    mapped_column: str
    present: bool


@dataclass(frozen=True)
class TickReplayLoadResult:
    source_path: Path
    schema_checks: tuple[TickSchemaCheck, ...]
    source_row_count: int
    snapshot_count: int
    symbols: tuple[str, ...]
    snapshots: tuple[QuoteSnapshot, ...]
    unsupported_symbols: tuple[str, ...]
    invalid_rows: tuple[str, ...]

    @property
    def missing_required_fields(self) -> tuple[str, ...]:
        return tuple(item.canonical_field for item in self.schema_checks if not item.present)

    @property
    def ok(self) -> bool:
        return (
            not self.missing_required_fields
            and not self.unsupported_symbols
            and not self.invalid_rows
            and self.snapshot_count > 0
        )


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace("_", "").replace("-", "")


def _build_field_map(fieldnames: list[str] | None) -> tuple[dict[str, str], tuple[TickSchemaCheck, ...]]:
    normalized = {_normalize_header(name): name for name in (fieldnames or [])}
    mapping: dict[str, str] = {}
    checks: list[TickSchemaCheck] = []
    for canonical in REQUIRED_TICK_FIELDS:
        mapped = ""
        for alias in FIELD_ALIASES[canonical]:
            candidate = normalized.get(_normalize_header(alias))
            if candidate:
                mapped = candidate
                mapping[canonical] = candidate
                break
        checks.append(TickSchemaCheck(canonical, mapped, bool(mapped)))
    return mapping, tuple(checks)


def _parse_datetime(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("empty datetime")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S", "%Y%m%d%H%M%S"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
    raise ValueError(f"unsupported datetime {text!r}")


def _float(row: dict[str, str], column: str, field: str) -> float:
    try:
        value = float(row[column])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{field} is not a number") from exc
    if value < 0:
        raise ValueError(f"{field} is negative")
    return value


def _int(row: dict[str, str], column: str, field: str) -> int:
    try:
        value = int(float(row[column]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{field} is not an integer") from exc
    if value < 0:
        raise ValueError(f"{field} is negative")
    return value


def _optional_float(row: dict[str, str], names: tuple[str, ...], default: float) -> float:
    normalized = {_normalize_header(key): key for key in row}
    for name in names:
        column = normalized.get(_normalize_header(name))
        if column and row.get(column, "").strip():
            return _float(row, column, name)
    return default


def _optional_int(row: dict[str, str], names: tuple[str, ...], default: int) -> int:
    normalized = {_normalize_header(key): key for key in row}
    for name in names:
        column = normalized.get(_normalize_header(name))
        if column and row.get(column, "").strip():
            return _int(row, column, name)
    return default


def _optional_bool(row: dict[str, str], names: tuple[str, ...], default: bool) -> bool:
    normalized = {_normalize_header(key): key for key in row}
    for name in names:
        column = normalized.get(_normalize_header(name))
        if column and row.get(column, "").strip():
            return row[column].strip().lower() in {"1", "true", "yes", "y", "stale"}
    return default


def load_tick_snapshots(path: Path, contracts_path: Path) -> TickReplayLoadResult:
    contracts = {contract.symbol: contract for contract in load_contracts(contracts_path)}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        field_map, schema_checks = _build_field_map(reader.fieldnames)
        rows = list(reader)

    missing = [item.canonical_field for item in schema_checks if not item.present]
    if missing:
        return TickReplayLoadResult(
            source_path=path,
            schema_checks=schema_checks,
            source_row_count=len(rows),
            snapshot_count=0,
            symbols=(),
            snapshots=(),
            unsupported_symbols=(),
            invalid_rows=tuple(f"missing required field: {field}" for field in missing),
        )

    invalid_rows: list[str] = []
    unsupported_symbols: list[str] = []
    prepared: list[tuple[int, datetime, str, float, float, int, int, int, int, float, str, bool, str]] = []

    for row_number, row in enumerate(rows, start=2):
        try:
            timestamp = _parse_datetime(row[field_map["datetime"]])
            symbol = row[field_map["symbol"]].strip()
            if not symbol:
                raise ValueError("symbol is empty")
            if symbol not in contracts:
                unsupported_symbols.append(symbol)
                continue
            bid = _float(row, field_map["bid_price1"], "bid_price1")
            ask = _float(row, field_map["ask_price1"], "ask_price1")
            if ask <= bid:
                raise ValueError("ask_price1 must be greater than bid_price1")
            bid_size = _int(row, field_map["bid_volume1"], "bid_volume1")
            ask_size = _int(row, field_map["ask_volume1"], "ask_volume1")
            last_price = _float(row, field_map["last_price"], "last_price")
            if not (bid <= last_price <= ask):
                raise ValueError("last_price must be inside bid_price1/ask_price1")
            _int(row, field_map["volume"], "volume")
            _int(row, field_map["open_interest"], "open_interest")
            trading_date = row[field_map["trading_date"]].strip()
            source = row[field_map["source"]].strip()
            if not trading_date:
                raise ValueError("trading_date is empty")
            if not source:
                raise ValueError("source is empty")
            bid_depth = _optional_int(row, ("bid_depth", "bid_depth1"), bid_size)
            ask_depth = _optional_int(row, ("ask_depth", "ask_depth1"), ask_size)
            quote_age_seconds = _optional_float(row, ("quote_age_seconds", "quote_age"), 0.0)
            freshness_status = row.get("freshness_status", "").strip().upper() or (
                "STALE" if quote_age_seconds > 30 else "FRESH"
            )
            is_stale = _optional_bool(row, ("is_stale", "stale"), quote_age_seconds > 30)
            prepared.append(
                (
                    row_number,
                    timestamp,
                    symbol,
                    bid,
                    ask,
                    bid_size,
                    ask_size,
                    bid_depth,
                    ask_depth,
                    quote_age_seconds,
                    freshness_status,
                    is_stale,
                    source,
                )
            )
        except ValueError as exc:
            invalid_rows.append(f"row {row_number}: {exc}")

    timestamp_ids = {timestamp: index for index, timestamp in enumerate(sorted({item[1] for item in prepared}), start=1)}
    snapshots: list[QuoteSnapshot] = []
    for (
        _row_number,
        timestamp,
        symbol,
        bid,
        ask,
        bid_size,
        ask_size,
        bid_depth,
        ask_depth,
        quote_age_seconds,
        freshness_status,
        is_stale,
        source,
    ) in prepared:
        contract = contracts[symbol]
        snapshots.append(
            QuoteSnapshot(
                snapshot_id=timestamp_ids[timestamp],
                timestamp=timestamp,
                timestamp_text=timestamp.isoformat(),
                symbol=symbol,
                underlying=contract.underlying,
                expiry=contract.expiry,
                strike=contract.strike,
                option_type=contract.option_type,
                bid=bid,
                ask=ask,
                bid_size=bid_size,
                ask_size=ask_size,
                bid_depth=bid_depth,
                ask_depth=ask_depth,
                quote_age_seconds=quote_age_seconds,
                freshness_status=freshness_status,
                is_stale=is_stale,
                source_note=source,
            )
        )
    snapshots.sort(key=lambda item: (item.timestamp, item.snapshot_id, item.symbol))
    return TickReplayLoadResult(
        source_path=path,
        schema_checks=schema_checks,
        source_row_count=len(rows),
        snapshot_count=len(snapshots),
        symbols=tuple(sorted({snapshot.symbol for snapshot in snapshots})),
        snapshots=tuple(snapshots),
        unsupported_symbols=tuple(sorted(set(unsupported_symbols))),
        invalid_rows=tuple(invalid_rows),
    )


def write_sanitized_tick_fixture_from_quote_replay(
    quote_fixture_path: Path,
    contracts_path: Path,
    output_path: Path,
) -> int:
    contracts = {contract.symbol: contract for contract in load_contracts(contracts_path)}
    snapshots = load_quote_snapshots(quote_fixture_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            lineterminator="\n",
            fieldnames=[
                "datetime",
                "symbol",
                "bid_price1",
                "bid_volume1",
                "ask_price1",
                "ask_volume1",
                "bid_depth",
                "ask_depth",
                "quote_age_seconds",
                "freshness_status",
                "is_stale",
                "last_price",
                "volume",
                "open_interest",
                "trading_date",
                "source",
            ],
        )
        writer.writeheader()
        for snapshot in snapshots:
            contract = contracts[snapshot.symbol]
            writer.writerow(
                {
                    "datetime": snapshot.timestamp_text,
                    "symbol": snapshot.symbol,
                    "bid_price1": f"{snapshot.bid:g}",
                    "bid_volume1": snapshot.bid_size,
                    "ask_price1": f"{snapshot.ask:g}",
                    "ask_volume1": snapshot.ask_size,
                    "bid_depth": snapshot.bid_depth,
                    "ask_depth": snapshot.ask_depth,
                    "quote_age_seconds": f"{snapshot.quote_age_seconds:g}",
                    "freshness_status": snapshot.freshness_status,
                    "is_stale": "true" if snapshot.is_stale else "false",
                    "last_price": f"{snapshot.mid:g}",
                    "volume": contract.volume,
                    "open_interest": contract.open_interest,
                    "trading_date": snapshot.timestamp.date().isoformat(),
                    "source": "TASK-011A_SANITIZED_FROM_LOCAL_QUOTE_FIXTURE",
                }
            )
    return len(snapshots)
