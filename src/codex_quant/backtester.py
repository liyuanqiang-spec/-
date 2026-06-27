from .schemas import SpreadCandidate


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
