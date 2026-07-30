#!/usr/bin/env python3
"""Cloud-only, fail-closed microcap research orchestrator (stdlib only)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import pathlib
import re
import statistics
import time
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from performance import summarize

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data"
STATE = ROOT / "state"
UA = "MicrocapAIResearchLab/1.1 135290796+3imed3imed@users.noreply.github.com"
TARGET_FORMS = {"8-K", "10-Q", "10-K", "6-K", "S-1", "S-3", "424B3", "424B4", "424B5", "DEF 14A", "4", "SC 13D", "SC 13G"}

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
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            time.sleep(0.25 * (2 ** attempt))
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except Exception as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


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


def sec_company_index() -> Evidence:
    url = "https://www.sec.gov/files/company_tickers.json"
    observed = now()
    try:
        raw = fetch(url)
        data = json.loads(raw)
        return Evidence("sec_company_index", "PASS", "SEC company index reachable and parseable", url, digest(raw), observed, len(data))
    except Exception as exc:
        return Evidence("sec_company_index", "BLOCKED", f"Collection error: {type(exc).__name__}", url, observed_at=observed)


def collect_recent_filings() -> tuple[list[dict[str, str]], Evidence]:
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&output=atom&count=100"
    observed = now()
    try:
        raw = fetch(url)
        root = ET.fromstring(raw)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        filings: list[dict[str, str]] = []
        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", default="", namespaces=ns)
            form = title.split(" - ", 1)[0].strip()
            if form not in TARGET_FORMS:
                continue
            link = entry.find("a:link", ns)
            filings.append({
                "form": form,
                "title": title,
                "accepted_or_updated": entry.findtext("a:updated", default="", namespaces=ns),
                "url": link.attrib.get("href", "") if link is not None else "",
                "known_time": observed,
            })
        return filings, Evidence("sec_recent_filings", "PASS", "Exact SEC feed timestamps captured for monitored forms", url, digest(raw), observed, len(filings))
    except Exception as exc:
        return [], Evidence("sec_recent_filings", "BLOCKED", f"Collection error: {type(exc).__name__}", url, observed_at=observed)


def parse_ftd_zip(payload: bytes) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        if not names:
            return []
        raw = archive.read(names[0]).decode("utf-8", errors="replace")
    rows = csv.DictReader(io.StringIO(raw), delimiter="|")
    parsed: list[dict[str, Any]] = []
    for row in rows:
        price_text = row.get("PRICE", ".")
        try:
            price = float(price_text)
        except (TypeError, ValueError):
            price = None
        parsed.append({
            "settlement_date": row.get("SETTLEMENT DATE", ""),
            "cusip": row.get("CUSIP", ""),
            "symbol": row.get("SYMBOL", ""),
            "fails": int(row.get("QUANTITY (FAILS)", "0") or 0),
            "description": row.get("DESCRIPTION", ""),
            "prior_close_reference": price,
        })
    return parsed


def collect_latest_ftd() -> tuple[list[dict[str, Any]], Evidence]:
    page_url = "https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data"
    observed = now()
    try:
        page = fetch(page_url)
        matches = re.findall(rb'href=["\']([^"\']*cnsfails(\d{6}[ab])\.zip)["\']', page, flags=re.I)
        if not matches:
            raise ValueError("No FTD archive links found")
        href, _ = max(matches, key=lambda item: item[1].lower())
        zip_url = urllib.parse.urljoin(page_url, href.decode("utf-8"))
        raw = fetch(zip_url)
        rows = parse_ftd_zip(raw)
        for row in rows:
            row["known_time"] = observed
            row["source"] = zip_url
        return rows, Evidence("sec_fails_to_deliver", "PASS", "Latest official aggregate FTD archive collected; FTD is not treated as short interest", zip_url, digest(raw), observed, len(rows))
    except Exception as exc:
        return [], Evidence("sec_fails_to_deliver", "BLOCKED", f"Collection error: {type(exc).__name__}", page_url, observed_at=observed)



def detect_universe_changes(current: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = sorted(STATE.glob("universe-*.json"))
    current_map = {row["symbol"]: row for row in current}
    if not snapshots:
        return {"status": "BASELINE", "previous_snapshot": None, "added": [], "removed": []}
    previous_path = snapshots[-1]
    previous = json.loads(previous_path.read_text(encoding="utf-8")).get("securities", [])
    previous_map = {row["symbol"]: row for row in previous}
    added_symbols = sorted(current_map.keys() - previous_map.keys())
    removed_symbols = sorted(previous_map.keys() - current_map.keys())
    return {
        "status": "COMPARED",
        "previous_snapshot": previous_path.name,
        "added": [current_map[symbol] for symbol in added_symbols],
        "removed": [previous_map[symbol] for symbol in removed_symbols],
    }

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
    changes = detect_universe_changes(universe)
    evidence.append(Evidence("prospective_universe_changes", "PASS", f"Compared snapshots: {len(changes['added'])} additions and {len(changes['removed'])} removals"))
    paper_metrics = summarize([], starting_equity=100.0, minimum_sample=policy["minimum_oos_trades"])
    filings, filings_evidence = collect_recent_filings()
    ftd, ftd_evidence = collect_latest_ftd()
    evidence.extend([sec_company_index(), filings_evidence, ftd_evidence])
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
    manifest = {
        "schema_version": "1.1.0",
        "run_id": os.getenv("GITHUB_RUN_ID", "manual-cloud-run"),
        "generated_at": now(),
        "code_commit": os.getenv("GITHUB_SHA", "unknown"),
        "policy_hash": digest(json.dumps(policy, sort_keys=True).encode()),
        "status": status,
        "live_execution_enabled": False,
        "universe_rows_current": len(universe),
        "recent_target_filings": len(filings),
        "latest_ftd_rows": len(ftd),
        "sub5_ftd_reference_rows": sum(1 for r in ftd if r["prior_close_reference"] is not None and r["prior_close_reference"] < 5),
        "universe_additions": len(changes["added"]),
        "universe_removals": len(changes["removed"]),
        "paper_performance": paper_metrics,
        "evidence": [asdict(e) for e in evidence],
        "opportunities": [],
        "message": "No opportunities published: scientific acceptance gates did not pass." if status != "PASS" else "All gates passed."
    }
    (OUT / "latest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    (STATE / f"universe-{stamp}.json").write_text(json.dumps({"observed_at": now(), "securities": universe}, separators=(",", ":")), encoding="utf-8")
    regulatory = {"observed_at": now(), "recent_filings": filings, "latest_ftd": ftd}
    (STATE / f"regulatory-{stamp}.json").write_text(json.dumps(regulatory, separators=(",", ":")), encoding="utf-8")
    (STATE / f"listing-events-{stamp}.json").write_text(json.dumps({"observed_at": now(), **changes}, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"status": status, "universe": len(universe), "filings": len(filings), "ftd": len(ftd), "opportunities": 0}))
    return manifest


if __name__ == "__main__":
    run()
