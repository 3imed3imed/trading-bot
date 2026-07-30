#!/usr/bin/env python3
"""Free current-market observation scan; never submits or recommends orders."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from dataclasses import asdict
from datetime import datetime, timezone

from public_market import PublicMarketRow, fetch_current_market

ROOT = pathlib.Path(__file__).resolve().parents[1]


def scan(rows: list[PublicMarketRow], config: dict, source_hash: str) -> dict:
    eligible = [
        row for row in rows
        if config["minimum_price"] <= row.last_price < config["price_ceiling"]
        and row.volume >= config.get("minimum_daily_volume", 100000)
    ]
    selected = sorted(
        (row for row in eligible if row.percent_change >= config["momentum_candidate_threshold"] * 100),
        key=lambda row: (row.percent_change, row.volume),
        reverse=True,
    )[:100]
    observed = max((row.observed_at for row in rows), default=datetime.now(timezone.utc).isoformat())
    candidates = [
        {
            **asdict(row),
            "classification": "UNVALIDATED_OBSERVATION",
            "tradable": False,
            "reason": "Current price/volume/momentum screen only; no validated edge or bid/ask execution evidence",
        }
        for row in selected
    ]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "market_observed_at": observed,
        "mode": "FREE_PUBLIC_CURRENT_SCAN",
        "source": "Nasdaq public stock screener",
        "source_hash": source_hash,
        "rows_received": len(rows),
        "under_5_liquid_rows": len(eligible),
        "candidate_count": len(candidates),
        "status": "OBSERVATIONS_AVAILABLE" if candidates else "NO_CURRENT_CANDIDATES",
        "execution_status": "BLOCKED_NO_BID_ASK",
        "orders_submitted": 0,
        "live_execution_enabled": False,
        "candidates": candidates,
        "disclaimer": "Candidates are observations, not recommendations. They cannot be promoted or traded without locked OOS validation and execution evidence.",
    }


def blocked_manifest(exc: Exception) -> dict:
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "FREE_PUBLIC_CURRENT_SCAN",
        "status": "BLOCKED",
        "reason": f"{type(exc).__name__}: {exc}",
        "rows_received": 0,
        "under_5_liquid_rows": 0,
        "candidate_count": 0,
        "execution_status": "BLOCKED_NO_MARKET_DATA",
        "orders_submitted": 0,
        "live_execution_enabled": False,
        "candidates": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "config" / "watchlist.json").read_text(encoding="utf-8"))
    try:
        rows, raw = fetch_current_market()
        result = scan(rows, config, hashlib.sha256(raw).hexdigest())
    except Exception as exc:
        result = blocked_manifest(exc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "rows": result["rows_received"], "candidates": result["candidate_count"], "orders": 0}))


if __name__ == "__main__":
    main()
