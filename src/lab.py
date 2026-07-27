#!/usr/bin/env python3
"""Cloud-only, fail-closed microcap research orchestrator (stdlib only)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import pathlib
import statistics
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data"
STATE = ROOT / "state"
UA = "MicrocapAIResearchLab/1.0 research-contact@example.invalid"

@dataclass(frozen=True)
class Evidence:
    stage: str
    status: str
    reason: str
    source: str | None = None
    content_hash: str | None = None
    observed_at: str | None = None
    rows: int | None = None


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_pipe(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8", errors="replace")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="|"))
    return [r for r in rows if r and not str(next(iter(r.values()), "")).startswith("File Creation Time")]


def collect_universe() -> tuple[list[dict[str, Any]], list[Evidence]]:
    observed = now()
    sources = [
        ("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", "NASDAQ"),
        ("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", "OTHER"),
    ]
    securities: list[dict[str, Any]] = []
    evidence: list[Evidence] = []
    for url, venue in sources:
        try:
            raw = fetch(url)
            rows = parse_pipe(raw)
            for row in rows:
                symbol = row.get("Symbol") or row.get("ACT Symbol")
                test = row.get("Test Issue", "N")
                name = row.get("Security Name", "")
                exchange = row.get("Exchange", venue)
                excluded = test == "Y" or any(x in name.upper() for x in [" ETF", "WARRANT", "RIGHT", " UNIT", "PREFERRED"])
                if symbol and not excluded:
                    securities.append({"symbol": symbol, "name": name, "exchange": exchange, "known_time": observed})
            evidence.append(Evidence("universe_current_snapshot", "PASS", "Authoritative current listing snapshot collected", url, digest(raw), observed, len(rows)))
        except Exception as exc:
            evidence.append(Evidence("universe_current_snapshot", "BLOCKED", f"Collection error: {type(exc).__name__}", url, observed_at=observed))
    evidence.append(Evidence("point_in_time_universe", "BLOCKED", "Current snapshots accumulate prospectively, but free sources do not provide complete historical constituents and delisted securities"))
    evidence.append(Evidence("delisted_security_coverage", "BLOCKED", "No complete authoritative free delisted-security master is configured"))
    return securities, evidence


def sec_health() -> Evidence:
    url = "https://www.sec.gov/files/company_tickers.json"
    observed = now()
    try:
        raw = fetch(url)
        data = json.loads(raw)
        return Evidence("sec_company_index", "PASS", "SEC company index reachable and parseable", url, digest(raw), observed, len(data))
    except Exception as exc:
        return Evidence("sec_company_index", "BLOCKED", f"Collection error: {type(exc).__name__}", url, observed_at=observed)


def statistical_gates(returns: list[float]) -> list[Evidence]:
    if len(returns) < 500:
        return [Evidence("sufficient_sample", "REJECTED", f"Need at least 500 locked OOS trades; received {len(returns)}")]
    mean = statistics.fmean(returns)
    return [Evidence("positive_expectancy", "PASS" if mean > 0 else "REJECTED", f"Locked OOS mean return={mean:.8f}")]


def critic(evidence: list[Evidence]) -> Evidence:
    failed = [e.stage for e in evidence if e.status != "PASS"]
    if failed:
        return Evidence("critic_approval", "REJECTED", "Mandatory evidence failed: " + ", ".join(sorted(set(failed))))
    return Evidence("critic_approval", "PASS", "All mandatory evidence gates passed")


def run() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    policy = json.loads((ROOT / "config" / "acceptance-policy.json").read_text(encoding="utf-8"))
    universe, evidence = collect_universe()
    evidence.append(sec_health())
    evidence.extend([
        Evidence("minute_trades_quotes", "BLOCKED", "Complete historical consolidated minute trades/quotes are not available from a configured lawful free source"),
        Evidence("historical_news", "BLOCKED", "Complete original, unrevised historical news bodies are not available from a configured lawful free source"),
        Evidence("execution_model", "BLOCKED", "Bid/ask and order-book evidence required for realistic fills is unavailable"),
        Evidence("model_discovery", "BLOCKED", "Model search prohibited until upstream point-in-time data gates pass"),
        Evidence("paper_trading_pass", "BLOCKED", "No scientifically accepted model exists"),
    ])
    evidence.extend(statistical_gates([]))
    evidence.append(critic(evidence))
    status = "PASS" if all(e.status == "PASS" for e in evidence) else "REJECTED"
    commit = os.getenv("GITHUB_SHA", "unknown")
    manifest = {
        "schema_version": "1.0.0",
        "run_id": os.getenv("GITHUB_RUN_ID", "manual-cloud-run"),
        "generated_at": now(),
        "code_commit": commit,
        "policy_hash": digest(json.dumps(policy, sort_keys=True).encode()),
        "status": status,
        "live_execution_enabled": False,
        "universe_rows_current": len(universe),
        "evidence": [asdict(e) for e in evidence],
        "opportunities": [],
        "message": "No opportunities published: scientific acceptance gates did not pass." if status != "PASS" else "All gates passed."
    }
    (OUT / "latest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = {"observed_at": now(), "securities": universe}
    (STATE / f"universe-{stamp}.json").write_text(json.dumps(snapshot, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"status": status, "universe": len(universe), "opportunities": 0}))
    return manifest


if __name__ == "__main__":
    run()
