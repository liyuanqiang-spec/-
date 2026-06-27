import unittest

from src.codex_quant.backtester import run_first_complete_simulation
from src.codex_quant.config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.risk_control import check_research_risk
from src.codex_quant.spread_calculator import calculate_vertical_spreads


class RiskControlTest(unittest.TestCase):
    def test_risk_checker_accepts_phase_one_simulation_only_mode(self):
        contracts = scan_contracts(
            load_contracts(SAMPLE_CONTRACTS),
            DEFAULT_MIN_VOLUME,
            DEFAULT_MAX_SPREAD_PCT,
        )
        candidates = calculate_vertical_spreads(contracts)
        simulations, summary = run_first_complete_simulation(
            contracts,
            candidates,
            "PHASE_1_SIMULATION_ONLY",
        )
        issues = check_research_risk(
            contracts,
            candidates,
            "PHASE_1_SIMULATION_ONLY",
            simulations,
            summary,
        )

        self.assertNotIn("BLOCKED: trading mode is not simulation-only", issues)
        self.assertIn("LOW_SAMPLE: candidate count is below 20", issues)

    def test_risk_checker_blocks_non_simulation_mode(self):
        issues = check_research_risk([], [], "REAL_TRADING")

        self.assertIn("BLOCKED: trading mode is not simulation-only", issues)


if __name__ == "__main__":
    unittest.main()
