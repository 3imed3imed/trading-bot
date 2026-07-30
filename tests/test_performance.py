import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from performance import Trade, summarize


class PerformanceTests(unittest.TestCase):
    def test_empty_ledger_reports_unknown_not_zero_edge(self):
        result = summarize([], starting_equity=100)
        self.assertEqual(result["status"], "INSUFFICIENT_OR_UNPROVEN")
        self.assertIsNone(result["win_rate"])
        self.assertEqual(result["net_profit"], 0)

    def test_core_metrics(self):
        result = summarize([Trade(0.10), Trade(-0.05), Trade(0.05), Trade(-0.02)], minimum_sample=4)
        self.assertEqual(result["trade_count"], 4)
        self.assertEqual(result["win_rate"], 0.5)
        self.assertAlmostEqual(result["average_win"], 0.075)
        self.assertAlmostEqual(result["average_loss"], -0.035)
        self.assertAlmostEqual(result["expectancy_per_trade"], 0.02)
        self.assertAlmostEqual(result["profit_factor"], 0.15 / 0.07)
        self.assertGreater(result["maximum_drawdown"], 0)

    def test_position_fraction_controls_equity_impact(self):
        full = summarize([Trade(0.10, 1.0)], minimum_sample=1)
        quarter = summarize([Trade(0.10, 0.25)], minimum_sample=1)
        self.assertAlmostEqual(full["ending_equity"], 110)
        self.assertAlmostEqual(quarter["ending_equity"], 102.5)

    def test_rejects_leverage_in_v1(self):
        with self.assertRaises(ValueError):
            summarize([Trade(0.10, 1.1)])

    def test_confidence_gate_rejects_small_samples(self):
        result = summarize([Trade(0.02)] * 20, minimum_sample=500)
        self.assertEqual(result["status"], "INSUFFICIENT_OR_UNPROVEN")


if __name__ == "__main__":
    unittest.main()
