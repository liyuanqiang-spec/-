import csv
from pathlib import Path

from .schemas import OptionContract


def load_contracts(path: Path) -> list[OptionContract]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f)
        return [
            OptionContract(
                symbol=row["symbol"],
                underlying=row["underlying"],
                expiry=row["expiry"],
                strike=float(row["strike"]),
                option_type=row["option_type"].upper(),
                bid=float(row["bid"]),
                ask=float(row["ask"]),
                volume=int(row["volume"]),
                open_interest=int(row["open_interest"]),
            )
            for row in rows
        ]


def scan_contracts(
    contracts: list[OptionContract],
    min_volume: int,
    max_spread_pct: float,
) -> list[OptionContract]:
    return [
        contract
        for contract in contracts
        if contract.bid > 0
        and contract.ask > contract.bid
        and contract.volume >= min_volume
        and contract.spread_pct <= max_spread_pct
    ]
