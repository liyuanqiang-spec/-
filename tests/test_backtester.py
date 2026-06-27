import unittest

from src.codex_quant.backtester import run_first_complete_simulation
from src.codex_quant.config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.spread_calculator import calculate_vertical_spreads


class BacktesterTest(unittest.TestCase):
    def test_first_complete_simulation_returns_dashboard_metrics(self):
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

        self.assertEqual(len(simulations), len(candidates))
        self.assertEqual(summary.contracts_scanned, len(contracts))
        self.assertEqual(summary.spread_candidates, len(candidates))
        self.assertEqual(summary.rejected_candidates, len([item for item in simulations if not item.accepted]))
        self.assertGreater(summary.average_simulated_edge, 0)
        self.assertGreaterEqual(summary.worst_simulated_slippage, 0)
        self.assertIn(summary.reliability, {"LOW_SAMPLE", "OK"})


if __name__ == "__main__":
    unittest.main()
