import unittest

from src.codex_quant.contract_scanner import load_contracts
from src.codex_quant.config import SAMPLE_CONTRACTS
from src.codex_quant.low_liquidity_scanner import low_volume_threshold, scan_low_liquidity_contracts


class LowLiquidityScannerTest(unittest.TestCase):
    def test_sample_scan_finds_inactive_contracts_with_open_interest(self):
        contracts = load_contracts(SAMPLE_CONTRACTS)
        candidates = scan_low_liquidity_contracts(contracts)
        symbols = [candidate.contract.symbol for candidate in candidates]

        self.assertEqual(low_volume_threshold(contracts), 61)
        self.assertEqual(symbols, ["AG2609C7400", "AG2608P6800", "AG2609C7200"])
        self.assertTrue(all(candidate.contract.open_interest > 0 for candidate in candidates))
        self.assertTrue(all(candidate.contract.volume <= 61 for candidate in candidates))


if __name__ == "__main__":
    unittest.main()
