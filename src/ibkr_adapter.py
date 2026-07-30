"""Interactive Brokers Client Portal Gateway adapter.

For individual IBKR accounts, an authenticated Client Portal Gateway session must
already exist. This adapter performs read-only readiness checks and never submits
orders. The gateway URL must be HTTPS and supplied through the cloud environment.
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IbkrSession:
    authenticated: bool
    connected: bool
    competing: bool
    account_ids: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.authenticated and self.connected and not self.competing and bool(self.account_ids)


def parse_auth_status(payload: dict[str, Any], accounts: list[dict[str, Any]] | None = None) -> IbkrSession:
    account_ids = tuple(
        str(row.get("accountId") or row.get("id"))
        for row in (accounts or [])
        if row.get("accountId") or row.get("id")
    )
    return IbkrSession(
        authenticated=bool(payload.get("authenticated", False)),
        connected=bool(payload.get("connected", False)),
        competing=bool(payload.get("competing", False)),
        account_ids=account_ids,
    )


def _gateway_url() -> str:
    value = os.getenv("IBKR_GATEWAY_URL", "").rstrip("/")
    if not value:
        raise RuntimeError("IBKR_GATEWAY_URL is not configured")
    if not value.startswith("https://"):
        raise RuntimeError("IBKR_GATEWAY_URL must use HTTPS")
    return value


def _get_json(path: str) -> Any:
    request = urllib.request.Request(
        _gateway_url() + path,
        headers={"Accept": "application/json", "User-Agent": "microcap-ai-research-lab/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def fetch_session() -> IbkrSession:
    auth = _get_json("/iserver/auth/status")
    accounts = _get_json("/portfolio/accounts") if auth.get("authenticated") else []
    return parse_auth_status(auth, accounts)


def public_status(session: IbkrSession) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "mode": "IBKR_PAPER_SESSION",
        "connection": "PASS" if session.ready else "BLOCKED",
        "reason": "IBKR paper brokerage session is ready" if session.ready else "IBKR paper brokerage session is not ready",
        "authenticated": session.authenticated,
        "connected": session.connected,
        "competing_session": session.competing,
        "account_count": len(session.account_ids),
        "orders_submitted": 0,
        "live_trading_enabled": False,
    }
