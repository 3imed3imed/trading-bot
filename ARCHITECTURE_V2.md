# Microcap AI Research Lab — Architecture v2

## Evidence-backed framework comparison

| Project | Strongest structure to adopt | Weakness to avoid |
|---|---|---|
| QuantConnect LEAN | Separate universe, alpha, portfolio construction, execution, risk, brokerage, data-feed, transaction, result and real-time handlers; event-driven validation; broker models | Large operational surface; correct results still depend on licensed, correctly normalized data and brokerage configuration |
| Microsoft Qlib | Point-in-time data support; explicit workflow; ExperimentManager → Experiment → Recorder hierarchy; stored parameters, metrics, artifacts and predictions; offline/online separation | Primarily a research platform; easy to misconfigure experiment/model artifact selection; example data is not a microcap point-in-time solution |
| VectorBT | Extremely fast vectorized hypothesis screening; explicit fees, slippage, partial/rejected orders; broad analytics and walk-forward tooling | Massive parameter search amplifies data snooping; vectorized fills can diverge from event-driven market mechanics |
| Lumibot | One strategy contract across backtest, paper and live modes; inspectable agent decisions; broker adapters; monitoring and kill switches | Convenient sample feeds and AI decisions can be mistaken for evidence; managed data/cloud and LLM usage are not fully free |
| Zipline Reloaded | Event-driven clock; asset lifetimes; exchange calendars; data bundles; portfolio/account ledger | Data ingestion is user-owned and legacy examples do not solve modern microcap coverage or live execution |
| FinRL / FinRL-X | Decoupled data, environment, agent and application layers; explicit train-test-trade flow; production version adds typed config and layered risk | Reinforcement learning is unstable, difficult to explain, and especially vulnerable to reward leakage and regime overfit |
| Backtesting.py | Small comprehensible strategy API; explicit spread, commission, margin and trade statistics | Single-system simplicity does not provide point-in-time security master, distributed experiments, robust portfolio simulation or production controls |

## Adopted architecture

```text
Cloud Scheduler
  -> Orchestrator
     -> Point-in-Time Data Gateway
     -> Universe Handler
     -> Feature Materializer
     -> Discovery Engine (vectorized, disposable)
     -> Experiment Recorder
     -> Locked Event Validator
     -> Alpha Handler
     -> Portfolio Constructor
     -> Risk Handler
     -> Execution Simulator
     -> Critic Council
     -> Promotion Controller
        -> Paper Broker Adapter
        -> Live Broker Adapter [physically disabled]
     -> Results / Monitoring
```

## Non-negotiable boundaries

1. Data observations use `event_time`, `known_time`, `ingested_at`, source and content hash.
2. Features and labels are different artifacts. A feature must be known by decision time.
3. Vectorized discovery can reject ideas but cannot approve a model.
4. Final approval uses event-driven simulation with asset lifetimes, calendars, bid/ask, capacity and delayed fills.
5. Backtest, paper and live use one immutable strategy interface; only adapters change.
6. Every experiment records code, data, policy, parameters, metrics, artifacts and parent experiment.
7. RL remains quarantined until deterministic baselines pass; it can never bypass explainability or critic gates.
8. Live mode requires an accepted model, paper evidence, broker authorization, risk limits and a separate enable token.
9. Unknown evidence is `BLOCKED`, never coerced to zero or `PASS`.
10. No framework-provided example dataset is treated as decision-grade microcap evidence.

## Promotion path

`DISCOVERY -> LOCKED_EVENT_BACKTEST -> PAPER -> LIVE_ELIGIBLE`

Promotion is monotonic, versioned, and reversible. LIVE execution remains disabled in the repository policy.
