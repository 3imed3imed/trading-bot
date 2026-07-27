# Free-source research register

Updated 2026-07-28 JST. Only lawful public sources are admitted. Availability does not imply decision-grade completeness.

| Source | Free evidence | Point-in-time posture | Decision-grade role |
|---|---|---|---|
| Nasdaq Trader Symbol Directory | Current Nasdaq and other-listed security master | Prospectively snapshotted by the lab; not a historical constituent database | Universe monitoring only |
| SEC EDGAR APIs | Filings, submissions metadata, XBRL facts; no API key | Filing/acceptance timestamps are usable when the endpoint is reachable | Regulatory and fundamental evidence |
| SEC Fails-to-Deliver archives | Settlement date, CUSIP, symbol, aggregate fails, reference price | Historical archives from 2004 with an important 2008 coverage break | Research feature only; never labeled short interest |
| FINRA Short Sale Volume | Off-exchange reported short-sale volume | Daily/monthly history; free non-commercial use | Partial flow feature only; not consolidated exchange volume and not short interest |
| GitHub Actions | Scheduled ephemeral compute | Run and artifact history | Orchestration and reproducibility |
| Git history | Versioned snapshots and manifests | Commit timestamps and hashes | Point-in-time evidence store for prospective collection |

## Rejected substitutions

- Current constituents backfilled into history: survivorship bias.
- Adjusted daily bars without original corporate-action records: possible future leakage.
- Scraped/revised news substituted for original publication bodies and timestamps: provenance failure.
- FTD or FINRA daily short volume called “short interest”: category error.
- Free delayed or single-venue quotes used to simulate consolidated executable fills: unrealistic execution.
- LLM-generated labels or price forecasts: prohibited.

## Current hard boundary

No complete lawful free source was found for the combined requirement of delisted US microcaps, historical point-in-time membership, consolidated one-minute trades and quotes, bid/ask and order book, full original historical news, historical float, and corporate-action-complete prices. Those gates remain blocked. The platform continues prospective evidence collection and publishes zero opportunities until the locked scientific policy passes.

## Primary documentation

- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC Fails-to-Deliver: https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data
- FINRA Short Sale Volume: https://www.finra.org/finra-data/browse-catalog/short-sale-volume
