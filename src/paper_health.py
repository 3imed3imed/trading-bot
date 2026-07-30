#!/usr/bin/env python3
"""Cloud-only paper-broker health check. Never places orders."""
from __future__ import annotations

import argparse
import json
import pathlib

from paper_broker import fetch_paper_account, public_status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = public_status(fetch_paper_account())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "mode": result["mode"],
        "connection": result["connection"],
        "orders": result["orders_submitted"],
    }))


if __name__ == "__main__":
    main()
