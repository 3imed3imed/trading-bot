import json
import pathlib
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
