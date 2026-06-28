import csv
import tempfile
import unittest
from pathlib import Path

from src.codex_quant.config import SAMPLE_CONTRACTS, TICK_REPLAY_FIXTURE, QUOTE_REPLAY_FIXTURE
from src.codex_quant.tick_replay_adapter import (
    load_tick_snapshots,
    write_sanitized_tick_fixture_from_quote_replay,
)


class TickReplayAdapterTest(unittest.TestCase):
    def test_write_and_load_sanitized_tick_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tick_smoke.csv"
            row_count = write_sanitized_tick_fixture_from_quote_replay(
                QUOTE_REPLAY_FIXTURE,
                SAMPLE_CONTRACTS,
                path,
            )
            result = load_tick_snapshots(path, SAMPLE_CONTRACTS)

        self.assertEqual(row_count, 12)
        self.assertTrue(result.ok)
        self.assertEqual(result.snapshot_count, 12)
        self.assertEqual(result.missing_required_fields, ())
        self.assertIn("AG2608C7200", result.symbols)

    def test_loader_accepts_common_tick_column_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aliases.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "ts",
                        "instrument_id",
                        "bid_price_1",
                        "bid_volume_1",
                        "ask_price_1",
                        "ask_volume_1",
                        "last",
                        "cum_volume",
                        "oi",
                        "trade_date",
                        "data_source",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "ts": "2026-06-28T09:30:00+08:00",
                        "instrument_id": "AG2608C7200",
                        "bid_price_1": "82",
                        "bid_volume_1": "18",
                        "ask_price_1": "86",
                        "ask_volume_1": "20",
                        "last": "84",
                        "cum_volume": "120",
                        "oi": "850",
                        "trade_date": "2026-06-28",
                        "data_source": "UNIT_TEST",
                    }
                )

            result = load_tick_snapshots(path, SAMPLE_CONTRACTS)

        self.assertTrue(result.ok)
        self.assertEqual(result.snapshot_count, 1)
        self.assertEqual(result.snapshots[0].symbol, "AG2608C7200")
        self.assertEqual(result.snapshots[0].bid, 82)

    def test_loader_reports_missing_required_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("datetime,symbol,bid_price1\n2026-06-28T09:30:00+08:00,AG2608C7200,82\n", encoding="utf-8")

            result = load_tick_snapshots(path, SAMPLE_CONTRACTS)

        self.assertFalse(result.ok)
        self.assertIn("ask_price1", result.missing_required_fields)

    def test_repository_fixture_loads_after_validation_script_runs(self):
        if not TICK_REPLAY_FIXTURE.exists():
            self.skipTest("TASK-011A tick fixture has not been generated yet")
        result = load_tick_snapshots(TICK_REPLAY_FIXTURE, SAMPLE_CONTRACTS)

        self.assertTrue(result.ok)
        self.assertEqual(result.snapshot_count, 12)


if __name__ == "__main__":
    unittest.main()
