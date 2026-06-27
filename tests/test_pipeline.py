import unittest

from src.codex_quant import run_pipeline
from src.codex_quant.backtester import run_simple_backtest
from src.codex_quant.config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, FIRST_COMPLETE_REPORT, SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.risk_control import check_research_risk
from src.codex_quant.spread_calculator import calculate_vertical_spreads


class PipelineTest(unittest.TestCase):
    def test_sample_pipeline_creates_candidates(self):
        contracts = scan_contracts(
            load_contracts(SAMPLE_CONTRACTS),
            DEFAULT_MIN_VOLUME,
            DEFAULT_MAX_SPREAD_PCT,
        )
        candidates = calculate_vertical_spreads(contracts)
        backtest = run_simple_backtest(candidates)
        issues = check_research_risk(contracts, candidates, "SIMULATION_ONLY")

        self.assertGreater(len(contracts), 0)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(backtest["reliability"], "LOW_SAMPLE")
        self.assertIn("LOW_SAMPLE: candidate count is below 20", issues)

    def test_run_pipeline_writes_first_complete_report(self):
        result = run_pipeline.run()

        self.assertEqual(result["report"], str(FIRST_COMPLETE_REPORT))
        self.assertGreater(result["contracts"], 0)
        self.assertGreater(result["candidates"], 0)
        self.assertIn("average_simulated_edge", result)
        self.assertTrue(FIRST_COMPLETE_REPORT.exists())


if __name__ == "__main__":
    unittest.main()
