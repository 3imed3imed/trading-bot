#!/usr/bin/env python3
"""Publish safe IBKR paper-session readiness evidence. Never places orders."""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone

from ibkr_adapter import fetch_session, public_status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = public_status(fetch_session())
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"mode": result["mode"], "connection": result["connection"], "orders": 0}))


if __name__ == "__main__":
    main()
