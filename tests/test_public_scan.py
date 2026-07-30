import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from public_market import parse_screener
from public_scan import blocked_manifest, scan


class PublicScanTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "data": {"table": {"rows": [
                {"symbol": "MOVE", "name": "Mover Inc", "lastsale": "$1.25", "pctchange": "8.50%", "volume": "2,000,000", "marketCap": "12000000", "country": "US", "sector": "Health Care", "industry": "Biotechnology"},
                {"symbol": "QUIET", "name": "Quiet Inc", "lastsale": "$2.00", "pctchange": "1.00%", "volume": "900,000", "marketCap": "50000000"},
                {"symbol": "THIN", "name": "Thin Inc", "lastsale": "$0.50", "pctchange": "25.00%", "volume": "100"},
                {"symbol": "HIGH", "name": "High Inc", "lastsale": "$8.00", "pctchange": "20.00%", "volume": "900,000"},
            ]}}
        }
        self.config = {"minimum_price": 0.10, "price_ceiling": 5.0, "minimum_daily_volume": 100000, "momentum_candidate_threshold": 0.03}

    def test_parser_normalizes_public_values(self):
        rows = parse_screener(self.payload, "2026-01-01T00:00:00+00:00")
        self.assertEqual(rows[0].symbol, "MOVE")
        self.assertEqual(rows[0].last_price, 1.25)
        self.assertEqual(rows[0].volume, 2000000)
        self.assertEqual(rows[0].percent_change, 8.5)

    def test_scan_separates_observation_from_opportunity(self):
        result = scan(parse_screener(self.payload), self.config, "hash")
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["candidates"][0]["symbol"], "MOVE")
        self.assertFalse(result["candidates"][0]["tradable"])
        self.assertEqual(result["orders_submitted"], 0)
        self.assertEqual(result["execution_status"], "BLOCKED_NO_BID_ASK")

    def test_failure_is_published_as_blocked_not_empty_success(self):
        result = blocked_manifest(RuntimeError("feed unavailable"))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["candidate_count"], 0)
        self.assertIn("RuntimeError", result["reason"])


if __name__ == "__main__":
    unittest.main()
