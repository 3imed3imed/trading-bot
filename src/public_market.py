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
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MicrocapAIResearchLab/1.0; +https://github.com/3imed3imed/trading-bot)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
}


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


def _fetch_page(offset: int, page_size: int) -> tuple[dict[str, Any], bytes]:
    query = urllib.parse.urlencode({"tableonly": "true", "limit": str(page_size), "offset": str(offset)})
    request = urllib.request.Request(f"{SCREENER_URL}?{query}", headers=HEADERS)
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            if attempt:
                time.sleep(2)
            with urllib.request.urlopen(request, timeout=25) as response:
                raw = response.read()
            return json.loads(raw), raw
        except Exception as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def fetch_current_market(limit: int = 10000, page_size: int = 1000) -> tuple[list[PublicMarketRow], bytes]:
    observed = datetime.now(timezone.utc).isoformat()
    rows_by_symbol: dict[str, PublicMarketRow] = {}
    page_hash_material: list[bytes] = []
    for offset in range(0, limit, page_size):
        payload, raw = _fetch_page(offset, page_size)
        page_hash_material.append(raw)
        page = parse_screener(payload, observed)
        for row in page:
            rows_by_symbol[row.symbol] = row
        raw_count = len((((payload.get("data") or {}).get("table") or {}).get("rows") or []))
        total_value = _number((payload.get("data") or {}).get("totalrecords"))
        if raw_count < page_size or (total_value is not None and offset + page_size >= int(total_value)):
            break
        time.sleep(0.25)
    if not rows_by_symbol:
        raise ValueError("Nasdaq screener returned no parseable rows")
    return list(rows_by_symbol.values()), b"\n".join(page_hash_material)
