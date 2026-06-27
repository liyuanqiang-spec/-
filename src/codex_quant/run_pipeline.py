from .backtester import run_simple_backtest
from .config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, LATEST_REPORT, SAMPLE_CONTRACTS, TRADING_MODE
from .contract_scanner import load_contracts, scan_contracts
from .report_writer import write_report
from .risk_control import check_research_risk
from .spread_calculator import calculate_vertical_spreads


def run() -> dict[str, object]:
    raw_contracts = load_contracts(SAMPLE_CONTRACTS)
    scanned = scan_contracts(raw_contracts, DEFAULT_MIN_VOLUME, DEFAULT_MAX_SPREAD_PCT)
    candidates = calculate_vertical_spreads(scanned)
    backtest = run_simple_backtest(candidates)
    risk_issues = check_research_risk(scanned, candidates, TRADING_MODE)
    write_report(LATEST_REPORT, scanned, candidates, backtest, risk_issues)
    return {
        "contracts": len(scanned),
        "candidates": len(candidates),
        "report": str(LATEST_REPORT),
        "risk_issues": risk_issues,
    }


if __name__ == "__main__":
    result = run()
    print(result)
