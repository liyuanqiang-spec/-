import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.codex_quant.config import SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.quant_baseline import (
    build_time_value_radar,
    infer_underlying_by_expiry,
    run_quant_baseline,
    score_spreads,
)
from src.codex_quant.spread_calculator import calculate_vertical_spreads
from src.codex_quant.backtester import run_first_complete_simulation


class QuantBaselineTest(unittest.TestCase):
    def test_time_value_radar_infers_underlying_and_flags(self):
        contracts = load_contracts(SAMPLE_CONTRACTS)
        levels = infer_underlying_by_expiry(contracts)
        rows = build_time_value_radar(contracts)

        self.assertAlmostEqual(levels[("AG", "2026-08-15")], 7246.0)
        self.assertEqual(len(rows), len(contracts))
        self.assertTrue(any(row.symbol == "AG2608C7200" and row.parity_deviation == 0 for row in rows))
        self.assertTrue(any("WIDE_SPREAD" in row.flags for row in rows))

    def test_score_spreads_uses_state_paths(self):
        contracts = load_contracts(SAMPLE_CONTRACTS)
        scanned = scan_contracts(contracts, 30, 0.25)
        candidates = calculate_vertical_spreads(scanned)
        simulations, _summary = run_first_complete_simulation(
            scanned,
            candidates,
            "PHASE_1_SIMULATION_ONLY",
        )
        scored = score_spreads(candidates, simulations)

        self.assertEqual(len(scored), len(candidates))
        self.assertTrue(scored[0].state_path[0] == "IDLE")
        self.assertTrue(all(item.second_leg_cost_estimate >= 0 for item in scored))

    def test_run_quant_baseline_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch("src.codex_quant.quant_baseline.QUANT_SYSTEM_GAP_REPORT", tmp_path / "gap.md"), patch(
                "src.codex_quant.quant_baseline.BACKTEST_BASELINE_REPORT",
                tmp_path / "baseline.md",
            ), patch(
                "src.codex_quant.quant_baseline.QUANT_BASELINE_REPLAY_CSV",
                tmp_path / "replay.csv",
            ):
                result = run_quant_baseline("- tests passed")

            self.assertGreater(len(result.scored_spreads), 0)
            self.assertTrue((tmp_path / "gap.md").exists())
            self.assertTrue((tmp_path / "baseline.md").exists())
            self.assertTrue((tmp_path / "replay.csv").exists())
            self.assertIn("TASK-010", (tmp_path / "gap.md").read_text(encoding="utf-8"))
            self.assertIn("Time-Value Radar", (tmp_path / "baseline.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
