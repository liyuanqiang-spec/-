import unittest

from src.codex_quant.config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, QUOTE_REPLAY_FIXTURE, SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.quote_replay import (
    estimate_passive_fill_probability,
    load_quote_snapshots,
    replay_spread_candidate,
    replay_vertical_spreads,
)
from src.codex_quant.spread_calculator import calculate_vertical_spreads


def _sample_candidates():
    contracts = scan_contracts(
        load_contracts(SAMPLE_CONTRACTS),
        DEFAULT_MIN_VOLUME,
        DEFAULT_MAX_SPREAD_PCT,
    )
    return calculate_vertical_spreads(contracts)


def _find_candidate(candidates, long_symbol, short_symbol):
    for candidate in candidates:
        if candidate.long_symbol == long_symbol and candidate.short_symbol == short_symbol:
            return candidate
    raise AssertionError(f"missing candidate {long_symbol}/{short_symbol}")


class QuoteReplayTest(unittest.TestCase):
    def test_loader_returns_ordered_snapshots_with_depth_and_freshness(self):
        snapshots = load_quote_snapshots(QUOTE_REPLAY_FIXTURE)

        self.assertEqual(len(snapshots), 12)
        self.assertEqual(snapshots, sorted(snapshots, key=lambda item: (item.timestamp, item.snapshot_id, item.symbol)))
        self.assertTrue(all(snapshot.bid_size > 0 and snapshot.ask_depth > 0 for snapshot in snapshots))
        self.assertTrue(any(snapshot.is_stale for snapshot in snapshots))

    def test_replay_measures_fill_timeout_staleness_and_repricing(self):
        candidates = _sample_candidates()
        snapshots = load_quote_snapshots(QUOTE_REPLAY_FIXTURE)
        results = replay_vertical_spreads(candidates, snapshots)
        by_pair = {
            (result.candidate.long_symbol, result.candidate.short_symbol): result
            for result in results
        }

        call = by_pair[("AG2608C7200", "AG2608C7400")]
        self.assertEqual(call.first_leg_symbol, "AG2608C7400")
        self.assertTrue(call.first_leg_filled)
        self.assertFalse(call.incomplete_leg)
        self.assertEqual(call.elapsed_seconds, 25)
        self.assertGreaterEqual(call.passive_fill_probability, 0.60)
        self.assertEqual(call.reprice_count, 1)
        self.assertEqual(call.second_leg_adverse_move, 2)
        self.assertIn("DONE", call.state_path)

        put = by_pair[("AG2608P7200", "AG2608P7000")]
        self.assertEqual(estimate_passive_fill_probability(snapshots[7]), 0.0)
        self.assertFalse(put.first_leg_filled)
        self.assertTrue(put.timed_out)
        self.assertTrue(put.incomplete_leg)
        self.assertGreater(put.stale_quote_count, 0)
        self.assertIn("STALE_QUOTE", put.state_path)
        self.assertIn("FIRST_LEG_TIMEOUT", put.state_path)

    def test_second_leg_protection_can_mark_incomplete_leg(self):
        candidates = _sample_candidates()
        snapshots = load_quote_snapshots(QUOTE_REPLAY_FIXTURE)
        candidate = _find_candidate(candidates, "AG2608C7200", "AG2608C7400")
        result = replay_spread_candidate(
            candidate,
            snapshots,
            max_second_leg_adverse_move_points=1.0,
        )

        self.assertIsNotNone(result)
        self.assertTrue(result.first_leg_filled)
        self.assertTrue(result.incomplete_leg)
        self.assertIn("SECOND_LEG_PROTECTION", result.state_path)
        self.assertIn("SECOND_LEG_ADVERSE_MOVE_LIMIT", result.risk_flags)


if __name__ == "__main__":
    unittest.main()
