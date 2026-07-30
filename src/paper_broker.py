"""Alpaca paper-account connectivity adapter.

This module verifies the broker control plane without submitting orders.
Credentials are read only from encrypted cloud environment variables.
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

PAPER_BASE_URL = "https://paper-api.alpaca.markets"


@dataclass(frozen=True)
class PaperAccount:
    account_id: str
    status: str
    currency: str
    cash: float
    equity: float
    buying_power: float
    trading_blocked: bool
    account_blocked: bool
    pattern_day_trader: bool

    @property
    def ready(self) -> bool:
        return (
            self.status.upper() == "ACTIVE"
            and not self.trading_blocked
            and not self.account_blocked
            and self.buying_power > 0
        )


def parse_account(payload: dict[str, Any]) -> PaperAccount:
    return PaperAccount(
        account_id=str(payload.get("id", "")),
        status=str(payload.get("status", "UNKNOWN")),
        currency=str(payload.get("currency", "USD")),
        cash=float(payload.get("cash", 0)),
        equity=float(payload.get("equity", 0)),
        buying_power=float(payload.get("buying_power", 0)),
        trading_blocked=bool(payload.get("trading_blocked", True)),
        account_blocked=bool(payload.get("account_blocked", True)),
        pattern_day_trader=bool(payload.get("pattern_day_trader", False)),
    )


def fetch_paper_account() -> PaperAccount:
    key = os.getenv("APCA_API_KEY_ID")
    secret = os.getenv("APCA_API_SECRET_KEY")
    if not key or not secret:
        raise RuntimeError("Alpaca paper credentials are not configured")
    request = urllib.request.Request(
        PAPER_BASE_URL + "/v2/account",
        headers={
            "APCA-API-KEY-ID": key,
            "APCA-API-SECRET-KEY": secret,
            "Accept": "application/json",
            "User-Agent": "microcap-ai-research-lab/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_account(json.loads(response.read()))


def public_status(account: PaperAccount) -> dict[str, Any]:
    """Return safe dashboard evidence without publishing the broker account ID."""
    data = asdict(account)
    data.pop("account_id", None)
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "ALPACA_PAPER_ACCOUNT",
        "connection": "PASS" if account.ready else "BLOCKED",
        "reason": "paper account is active and funded" if account.ready else "paper account is not ready",
        "account": data,
        "orders_submitted": 0,
        "live_trading_enabled": False,
    }
