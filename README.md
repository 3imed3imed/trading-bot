# Microcap AI Research Lab

A cloud-only, evidence-first research platform for testing whether a statistically valid edge exists in US-listed stocks below $5.

This is **not a trading bot**. The system is deliberately fail-closed. It currently publishes no opportunities because a complete point-in-time historical microcap dataset with delisted securities, consolidated minute trades/quotes, historical unrevised news, float history, and realistic execution evidence is not available from a lawful, complete, entirely free source.

## What runs autonomously

- Weekday GitHub Actions cloud schedule
- Nasdaq Trader current security-master snapshots accumulated through Git history
- SEC company-index availability and provenance checks
- Content hashing, timestamps, code/policy versioning, and run manifests
- Mandatory evidence gates and independent critic rejection
- Remote safety tests before publication
- Static evidence dashboard under `docs/`
- Live execution permanently disabled

## Scientific behavior

Missing data is not zero-filled or inferred. Current constituents are never presented as historical constituents. Models do not run until point-in-time and execution-data gates pass. Any failed or unknown mandatory gate produces zero opportunities.

See [ARCHITECTURE.md](ARCHITECTURE.md) and [config/acceptance-policy.json](config/acceptance-policy.json).

## Cloud operation

The workflow `.github/workflows/research-lab.yml` runs on GitHub-hosted infrastructure only. It can also be dispatched from the GitHub Actions page. The runner is ephemeral; durable evidence is committed to Git and attached as a workflow artifact.

## Current conclusion

`REJECTED / BLOCKED BY DATA EVIDENCE` is the scientifically correct result under the simultaneous requirements of complete coverage, realistic microstructure validation, no paid data, and no local infrastructure. The laboratory will continue accumulating prospective authoritative snapshots without claiming an edge.
