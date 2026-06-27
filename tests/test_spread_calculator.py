import unittest

from src.codex_quant.config import DEFAULT_MAX_SPREAD_PCT, DEFAULT_MIN_VOLUME, SAMPLE_CONTRACTS
from src.codex_quant.contract_scanner import load_contracts, scan_contracts
from src.codex_quant.spread_calculator import calculate_vertical_spreads


class SpreadCalculatorTest(unittest.TestCase):
    def test_sample_vertical_spreads_are_adjacent_and_positive_width(self):
        contracts = scan_contracts(
            load_contracts(SAMPLE_CONTRACTS),
            DEFAULT_MIN_VOLUME,
            DEFAULT_MAX_SPREAD_PCT,
        )
        candidates = calculate_vertical_spreads(contracts)

        self.assertEqual(len(candidates), 4)
        self.assertTrue(all(candidate.width > 0 for candidate in candidates))
        self.assertTrue(all(candidate.net_debit > 0 for candidate in candidates))
        self.assertEqual(
            {(candidate.underlying, candidate.expiry, candidate.option_type) for candidate in candidates},
            {("AG", "2026-08-15", "C"), ("AG", "2026-08-15", "P"), ("AG", "2026-09-15", "C")},
        )


if __name__ == "__main__":
    unittest.main()
