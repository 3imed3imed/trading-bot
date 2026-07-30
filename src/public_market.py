#!/usr/bin/env python3
"""Credential-free current US listing snapshot from Nasdaq's public screener."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

SCREENER_URL = "https://api.nasdaq.com/api/screener/stocks"


@dataclass(frozen=True)
class PublicMarketRow:
    symbol: str
    name: str
    last_price: float
    percent_change: float
    volume: int
    market_cap: float | None
    country: str
    sector: str
    industry: str
    observed_at: str


def _number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if not text or text in {"--", "N/A", "nan"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_screener(payload: dict[str, Any], observed_at: str | None = None) -> list[PublicMarketRow]:
    observed = observed_at or datetime.now(timezone.utc).isoformat()
    raw_rows = (((payload.get("data") or {}).get("table") or {}).get("rows") or [])
    parsed: list[PublicMarketRow] = []
    for row in raw_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        price = _number(row.get("lastsale"))
        change = _number(row.get("pctchange"))
        volume = _number(row.get("volume"))
        if not symbol or price is None or change is None or volume is None:
            continue
        parsed.append(PublicMarketRow(
            symbol=symbol,
            name=str(row.get("name") or "").strip(),
            last_price=price,
            percent_change=change,
            volume=max(0, int(volume)),
            market_cap=_number(row.get("marketCap")),
            country=str(row.get("country") or "").strip(),
            sector=str(row.get("sector") or "").strip(),
            industry=str(row.get("industry") or "").strip(),
            observed_at=observed,
        ))
    return parsed


def fetch_current_market(limit: int = 10000) -> tuple[list[PublicMarketRow], bytes]:
    query = urllib.parse.urlencode({"tableonly": "true", "limit": str(limit), "offset": "0", "download": "true"})
    request = urllib.request.Request(
        f"{SCREENER_URL}?{query}",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; MicrocapAIResearchLab/1.0; +https://github.com/3imed3imed/trading-bot)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            if attempt:
                time.sleep(2 ** attempt)
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read()
            rows = parse_screener(json.loads(raw))
            if not rows:
                raise ValueError("Nasdaq screener returned no parseable rows")
            return rows, raw
        except Exception as exc:
            last_error = exc
    assert last_error is not None
    raise last_error
