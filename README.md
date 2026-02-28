# Signal Intelligence Hub

Production-grade signal aggregation, verification, ranking, and consensus web app.

## What is implemented

- Next.js TypeScript frontend (dashboard/signals/sources/analytics/settings/connector status).
- PostgreSQL + Prisma schema with immutable raw payload storage and raw payload hash.
- Redis + BullMQ queue workers for outcome resolution and scoring recomputation.
- Real Binance market data (REST candles/ticker).
- Connectors:
  - TradingView webhook (`/api/ingest/tradingview`) with API key and optional HMAC validation.
  - Telegram forward webhook (`/api/ingest/telegram`) compliant-forward parsing only.
  - CSV import (`/api/ingest/csv`).
  - Generic webhook (`/api/ingest/generic`).
- Dedup, audit logging, retry-ready queue primitives, connector status visibility.
- Consensus explainability panel and conflict detector flag.

## Required fields per signal

Stored in DB and normalized:
- `sourceId, symbol, timeframe, side, createdAt, entry, stopLoss, takeProfit, confidenceRaw, verificationTier, rawPayload`

Additional: `canonicalSymbol`, `rawPayloadHash`, `dedupKey`, `confidenceScore`, outcome relation.

## Phase checkpoints

1. **Phase 1**: Auth/RBAC baseline + DB + UI skeleton + market data chart.
2. **Phase 2**: TradingView webhook ingest + real-time pub/sub broadcast.
3. **Phase 3**: Outcome engine + source performance metrics.
4. **Phase 4**: Telegram forward + CSV import.
5. **Phase 5**: Source credibility scoring + analytics + explainability.

## Local run

```bash
cp .env.example .env
npm install
npx prisma migrate dev --name init
npm run seed
npm run dev
npm run worker
npx tsx src/realtime/gateway.ts
```

App: `http://localhost:3000`
Realtime gateway: `http://localhost:4001`

## Docker run

```bash
docker compose up --build
```

## Connector status policy

- `SUPPORTED`: fully implemented official/allowed connector.
- `PARTIAL`: officially constrained; ingest via allowed exports/integrations.
- `NOT_AVAILABLE`: no lawful official interface.

No illegal scraping is used.

TradingView connector supports API key plus optional `x-signature` HMAC (sha256) using `TRADINGVIEW_HMAC_SECRET`.

## Security and compliance

- API keys should be encrypted before persistence (schema supports credentials table).
- RBAC helper present (`ADMIN` vs `USER`) for admin operations.
- Audit log written for ingestion success/failure events.
- Disclaimer in UI: consensus is informational and not guaranteed profit.
