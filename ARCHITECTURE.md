# Microcap AI Research Lab — Cloud v1

## Scientific contract

This repository is a research system, not a trading bot. It is fail-closed: absence, ambiguity, stale provenance, point-in-time uncertainty, leakage, insufficient sample size, or failed robustness tests produce `REJECTED`, never a trade.

## Free cloud architecture

GitHub is the v1 cloud control plane:

- GitHub Actions: scheduled remote compute and orchestration
- Git history: immutable, point-in-time versioning of source snapshots and experiment manifests
- Action artifacts: reproducible run outputs
- GitHub Pages: read-only monitoring dashboard
- SEC EDGAR and Nasdaq Trader: authoritative free regulatory and security-master inputs

No job depends on a user's desktop. The runner filesystem is ephemeral and is not a system of record.

## Agents

Agents are deterministic pipeline stages with typed evidence envelopes: infrastructure, market-data, SEC, news, corporate-actions, float, short-interest, features, NLP extraction, discovery, ML, validation, backtest, statistics, risk, critic, paper, execution, and monitoring. Every stage reports `PASS`, `REJECTED`, or `BLOCKED`; downstream promotion requires all mandatory stages to pass.

## Promotion state machine

`RESEARCH -> LOCKED_TEST -> PAPER -> LIVE_ELIGIBLE`

LIVE is permanently disabled in v1. Promotion requires multi-year walk-forward OOS evidence, locked-test success, positive net expectancy under base and doubled costs, delayed-entry robustness, stable strata, minimum sample size, multiplicity control, reproducible provenance, and critic approval.

## Free-tier limitation

A complete historical US microcap dataset containing delisted symbols, point-in-time constituents, consolidated one-minute trades/quotes, bid/ask, full historical unrevised news bodies, float history, and executable order-book data is not lawfully available as a complete free source. The lab records this as a blocking evidence gap. It must not infer, fabricate, backfill from current constituents, or publish opportunities until adequate licensed point-in-time sources are configured.

## Data model

Every observation carries `event_time`, `known_time`, `ingested_at`, `source`, `source_version`, and `content_hash`. Training features must satisfy `known_time <= decision_time`; labels live in a separate namespace and are joined only after feature materialization. Corporate actions are stored as events rather than destructively rewriting history.

## Reproducibility

Each run writes a manifest containing source URLs, retrieval timestamps, hashes, policy version, code commit, gate results, and rejection reasons. Scheduled snapshots committed to Git preserve the observed-as-of record. CI runs unit tests before any publication.
