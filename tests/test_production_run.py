import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from alpaca_adapter import parse_snapshots
from production_run import run

class ProductionRunTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / "fixtures" / "alpaca_iex_snapshot.json").read_bytes()
        self.snapshots = parse_snapshots(json.loads(self.raw))
        self.config = json.loads((ROOT / "config" / "watchlist.json").read_text())

    def test_real_connector_contract_parses(self):
        row = self.snapshots[0]
        self.assertEqual(row.symbol, "SNDL")
        self.assertAlmostEqual(row.trade_price, 1.195)
        self.assertLess(row.daily_return, 0)

    def test_end_to_end_run_rejects_when_no_signal(self):
        result = run(self.snapshots, self.config, "fixture-hash", fixture=True)
        self.assertEqual(result["stages"]["market_data"]["status"], "PASS")
        self.assertEqual(result["stages"]["universe"]["status"], "PASS")
        self.assertEqual(result["stages"]["candidate_signal"]["status"], "REJECTED")
        self.assertEqual(result["stages"]["execution_feasibility"]["status"], "BLOCKED")
        self.assertEqual(result["promotion"]["status"], "REJECTED")
        self.assertEqual(result["orders_submitted"], 0)

    def test_positive_candidate_reaches_execution_model(self):
        config = dict(self.config)
        config["momentum_candidate_threshold"] = -0.02
        result = run(self.snapshots, config, "fixture-hash", fixture=True)
        self.assertEqual(result["stages"]["candidate_signal"]["status"], "PASS")
        self.assertEqual(result["stages"]["execution_feasibility"]["status"], "PASS")
        self.assertTrue(result["fill_estimates"][0]["feasible"])
        self.assertEqual(result["orders_submitted"], 0)

if __name__ == "__main__":
    unittest.main()
