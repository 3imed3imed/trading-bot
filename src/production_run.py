#!/usr/bin/env python3
"""Real end-to-end scan path: market adapter -> gates -> execution -> promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from dataclasses import asdict
from datetime import datetime, timezone

from alpaca_adapter import Snapshot, fetch_iex_snapshots, parse_snapshots
from contracts import GateDecision, Status
from execution import Quote, estimate_market_buy
from orchestrator import Pipeline, Stage, promotion_decision

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(snapshots: list[Snapshot], config: dict, source_hash: str, fixture: bool = False) -> dict:
    candidates: list[dict] = []
    fills: list[dict] = []

    def data_stage(_):
        return GateDecision("market_data", Status.PASS if snapshots else Status.BLOCKED, f"received {len(snapshots)} IEX snapshots", (source_hash,) if snapshots else ())

    def universe_stage(_):
        eligible = [row for row in snapshots if config["minimum_price"] <= row.trade_price < config["price_ceiling"]]
        candidates.extend({"symbol": row.symbol, "price": row.trade_price, "daily_return": row.daily_return} for row in eligible)
        status = Status.PASS if eligible else Status.REJECTED
        return GateDecision("universe", status, f"{len(eligible)} symbols satisfy price policy", tuple(row.symbol for row in eligible))

    def signal_stage(_):
        selected = [row for row in candidates if row["daily_return"] >= config["momentum_candidate_threshold"]]
        for row in candidates:
            row["candidate"] = row in selected
        status = Status.PASS if selected else Status.REJECTED
        return GateDecision("candidate_signal", status, f"{len(selected)} deterministic research candidates", tuple(row["symbol"] for row in selected))

    def execution_stage(_):
        selected_symbols = {row["symbol"] for row in candidates if row.get("candidate")}
        for snapshot in snapshots:
            if snapshot.symbol not in selected_symbols:
                continue
            age = 0.0 if fixture else max(0.0, (datetime.now(timezone.utc) - snapshot.trade_time).total_seconds())
            estimate = estimate_market_buy(
                Quote(snapshot.bid, snapshot.ask, snapshot.bid_size, snapshot.ask_size, age),
                config["order_quantity"], snapshot.minute_volume, config["maximum_participation"]
            )
            fills.append({"symbol": snapshot.symbol, **asdict(estimate)})
        feasible = [row for row in fills if row["feasible"] and (row["spread_bps"] or 0) <= config["maximum_spread_bps"]]
        status = Status.PASS if feasible else Status.REJECTED
        return GateDecision("execution_feasibility", status, f"{len(feasible)} candidates pass quote/capacity limits", tuple(row["symbol"] for row in feasible))

    pipeline = Pipeline([
        Stage("market_data", (), data_stage),
        Stage("universe", ("market_data",), universe_stage),
        Stage("candidate_signal", ("universe",), signal_stage),
        Stage("execution_feasibility", ("candidate_signal",), execution_stage),
    ])
    decisions = pipeline.execute()
    promotion = promotion_decision(decisions, ["market_data", "universe", "candidate_signal", "execution_feasibility"])
    accepted = promotion.status is Status.PASS and config.get("live_orders_enabled") is True and not fixture
    return {
        "schema_version": "2.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "FIXTURE_SMOKE" if fixture else "LIVE_MARKET_SCAN",
        "source_hash": source_hash,
        "stages": {name: {"status": result.status.value, "reason": result.reason, "evidence": result.evidence} for name, result in decisions.items()},
        "promotion": {"status": promotion.status.value, "reason": promotion.reason},
        "candidates": candidates,
        "fill_estimates": fills,
        "orders_submitted": 0,
        "live_orders_enabled": False,
        "accepted_for_order_submission": accepted,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "config" / "watchlist.json").read_text(encoding="utf-8"))
    if args.fixture:
        raw = args.fixture.read_bytes()
        snapshots = parse_snapshots(json.loads(raw))
        fixture = True
    else:
        snapshots = fetch_iex_snapshots(config["symbols"])
        raw = json.dumps([asdict(row) for row in snapshots], default=str, sort_keys=True).encode()
        fixture = False
    result = run(snapshots, config, hashlib.sha256(raw).hexdigest(), fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"mode": result["mode"], "candidates": len(result["candidates"]), "orders": 0, "promotion": result["promotion"]["status"]}))

if __name__ == "__main__":
    main()
