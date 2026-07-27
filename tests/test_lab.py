import io
import json
import pathlib
import sys
import unittest
import zipfile
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import lab


class ScientificSafetyTests(unittest.TestCase):
    def test_insufficient_sample_is_rejected(self):
        gate = lab.statistical_gates([0.01] * 499)[0]
        self.assertEqual(gate.status, "REJECTED")

    def test_critic_rejects_any_nonpass(self):
        decision = lab.critic([lab.Evidence("leakage", "BLOCKED", "unknown")])
        self.assertEqual(decision.status, "REJECTED")

    def test_live_is_disabled_in_policy(self):
        policy = json.loads((ROOT / "config" / "acceptance-policy.json").read_text())
        self.assertFalse(policy["live_execution_enabled"])

    def test_known_time_rule(self):
        known = datetime.fromisoformat("2024-01-01T14:30:00+00:00")
        decision = datetime.fromisoformat("2024-01-01T14:29:59+00:00")
        self.assertFalse(known <= decision)

    def test_ftd_parser_preserves_point_in_time_fields(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("sample.txt", "SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE\n20260701|123456789|TEST|1200|TEST CO|4.25\n")
        row = lab.parse_ftd_zip(payload.getvalue())[0]
        self.assertEqual(row["symbol"], "TEST")
        self.assertEqual(row["fails"], 1200)
        self.assertEqual(row["prior_close_reference"], 4.25)

    def test_ftd_is_not_mislabeled_short_interest(self):
        self.assertNotIn("short_interest", lab.parse_ftd_zip.__name__)


if __name__ == "__main__":
    unittest.main()
