import argparse

from .backtester import run_first_complete_simulation, run_simple_backtest
from .config import (
    DEFAULT_MAX_SPREAD_PCT,
    DEFAULT_MIN_VOLUME,
    FIRST_COMPLETE_REPORT,
    FIRST_COMPLETE_SUMMARY,
    LATEST_REPORT,
    SAMPLE_CONTRACTS,
    TRADING_MODE,
)
from .contract_scanner import load_contracts, scan_contracts
from .report_writer import (
    write_first_complete_simulation_report,
    write_report,
    write_simulation_summary_json,
)
from .risk_control import check_research_risk
from .spread_calculator import calculate_vertical_spreads


def run() -> dict[str, object]:
    raw_contracts = load_contracts(SAMPLE_CONTRACTS)
    scanned = scan_contracts(raw_contracts, DEFAULT_MIN_VOLUME, DEFAULT_MAX_SPREAD_PCT)
    candidates = calculate_vertical_spreads(scanned)
    simulations, summary = run_first_complete_simulation(scanned, candidates, TRADING_MODE)
    risk_issues = check_research_risk(scanned, candidates, TRADING_MODE, simulations, summary)
    backtest = run_simple_backtest(candidates)
    write_report(LATEST_REPORT, scanned, candidates, backtest, risk_issues)
    command = "python3 -m src.codex_quant.run_pipeline --first-complete-simulation"
    write_first_complete_simulation_report(
        FIRST_COMPLETE_REPORT,
        raw_contracts,
        scanned,
        candidates,
        simulations,
        summary,
        risk_issues,
        command,
    )
    write_simulation_summary_json(FIRST_COMPLETE_SUMMARY, summary, risk_issues)
    return {
        "contracts": len(scanned),
        "candidates": len(candidates),
        "rejected_candidates": summary.rejected_candidates,
        "average_simulated_edge": summary.average_simulated_edge,
        "worst_simulated_slippage": summary.worst_simulated_slippage,
        "report": str(FIRST_COMPLETE_REPORT),
        "risk_issues": risk_issues,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the local simulation-only silver option pipeline.")
    parser.add_argument(
        "--first-complete-simulation",
        action="store_true",
        help="run the TASK-007 complete sample-data simulation report",
    )
    parser.parse_args()
    result = run()
    print(result)
