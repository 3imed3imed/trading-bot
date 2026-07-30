import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from contracts import DataEnvelope, GateDecision, Signal, Status
from execution import Quote, estimate_market_buy
from experiments import create_run
from orchestrator import Pipeline, Stage, promotion_decision

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

class ContractTests(unittest.TestCase):
    def test_future_information_is_rejected(self):
        row = DataEnvelope(NOW, NOW + timedelta(minutes=2), NOW + timedelta(minutes=3), "source", "hash", {})
        with self.assertRaises(ValueError):
            row.validate_for_decision(NOW + timedelta(minutes=1))

    def test_signal_requires_evidence(self):
        with self.assertRaises(ValueError):
            Signal("s1", "TEST", NOW, 1, 0.7, (), "price below stop")

class PipelineTests(unittest.TestCase):
    def test_failed_upstream_blocks_downstream_without_running_it(self):
        called = []
        stages = [
            Stage("data", (), lambda _: GateDecision("data", Status.REJECTED, "bad data")),
            Stage("model", ("data",), lambda _: called.append(True) or GateDecision("model", Status.PASS, "ok", ("x",))),
        ]
        result = Pipeline(stages).execute()
        self.assertEqual(result["model"].status, Status.BLOCKED)
        self.assertEqual(called, [])

    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            Pipeline([Stage("a", ("b",), lambda _: None), Stage("b", ("a",), lambda _: None)])

    def test_promotion_requires_every_gate(self):
        result = {"a": GateDecision("a", Status.PASS, "ok", ("hash",))}
        self.assertEqual(promotion_decision(result, ["a", "b"]).status, Status.REJECTED)

class ExecutionTests(unittest.TestCase):
    def test_capacity_rejects_unrealistic_fill(self):
        quote = Quote(1.00, 1.04, 1000, 100, 0.5)
        fill = estimate_market_buy(quote, quantity=200, minute_volume=5000)
        self.assertFalse(fill.feasible)

    def test_valid_fill_charges_spread_and_impact(self):
        quote = Quote(1.00, 1.02, 1000, 1000, 0.5)
        fill = estimate_market_buy(quote, quantity=50, minute_volume=10000)
        self.assertTrue(fill.feasible)
        self.assertGreater(fill.estimated_price, quote.ask)
        self.assertGreater(fill.slippage_bps, fill.spread_bps / 2)

class ExperimentTests(unittest.TestCase):
    def test_run_requires_data_provenance(self):
        with self.assertRaises(ValueError):
            create_run(experiment_id="e", run_id="r", code_commit="c", data_hashes=(), policy_hash="p", parameters={}, metrics={}, artifacts=(), mode="DISCOVERY")

    def test_fingerprint_is_stable_for_record(self):
        run = create_run(experiment_id="e", run_id="r", code_commit="c", data_hashes=("d",), policy_hash="p", parameters={"x": 1}, metrics={"m": 2}, artifacts=("a",), mode="DISCOVERY")
        self.assertEqual(run.fingerprint, run.fingerprint)

if __name__ == "__main__":
    unittest.main()
