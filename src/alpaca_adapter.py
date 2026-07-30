"""Alpaca IEX adapter. Credentials are read only from cloud environment variables."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class Snapshot:
    symbol: str
    trade_time: datetime
    trade_price: float
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    minute_volume: int
    daily_close: float
    previous_close: float

    @property
    def daily_return(self) -> float:
        return self.daily_close / self.previous_close - 1


def parse_snapshots(payload: dict[str, Any]) -> list[Snapshot]:
    source = payload.get("snapshots", payload)
    rows: list[Snapshot] = []
    for symbol, item in source.items():
        trade = item.get("latest_trade") or item.get("latestTrade") or {}
        quote = item.get("latest_quote") or item.get("latestQuote") or {}
        minute = item.get("minute_bar") or item.get("minuteBar") or {}
        daily = item.get("daily_bar") or item.get("dailyBar") or {}
        previous = item.get("previous_daily_bar") or item.get("prevDailyBar") or {}
        def value(obj: dict[str, Any], *names: str, default: Any = None) -> Any:
            for name in names:
                if name in obj:
                    return obj[name]
            return default
        timestamp = value(trade, "timestamp", "t")
        if not timestamp:
            continue
        rows.append(Snapshot(
            symbol=symbol,
            trade_time=datetime.fromisoformat(str(timestamp).replace("Z", "+00:00")),
            trade_price=float(value(trade, "price", "p")),
            bid=float(value(quote, "bid_price", "bp")),
            ask=float(value(quote, "ask_price", "ap")),
            bid_size=int(value(quote, "bid_size", "bs", default=0)),
            ask_size=int(value(quote, "ask_size", "as", default=0)),
            minute_volume=int(value(minute, "volume", "v", default=0)),
            daily_close=float(value(daily, "close", "c")),
            previous_close=float(value(previous, "close", "c")),
        ))
    return rows


def fetch_iex_snapshots(symbols: list[str]) -> list[Snapshot]:
    key = os.getenv("APCA_API_KEY_ID")
    secret = os.getenv("APCA_API_SECRET_KEY")
    if not key or not secret:
        raise RuntimeError("Alpaca cloud secrets are not configured")
    query = urllib.parse.urlencode({"symbols": ",".join(symbols), "feed": "iex"})
    request = urllib.request.Request(
        "https://data.alpaca.markets/v2/stocks/snapshots?" + query,
        headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_snapshots(json.loads(response.read()))
