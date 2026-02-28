import { OutcomeStatus, Side } from "@prisma/client";
import { prisma } from "./prisma";
import { fetchBinanceCandles } from "./market";

export async function resolveSignalOutcome(signalId: string) {
  const signal = await prisma.signal.findUnique({ where: { id: signalId }, include: { outcomes: true } });
  if (!signal || !signal.outcomes[0]) return;

  const outcome = signal.outcomes[0];
  if (outcome.status !== OutcomeStatus.PENDING) return;

  const now = new Date();
  const candles = await fetchBinanceCandles(signal.canonicalSymbol, mapTf(signal.timeframe), 500);
  const future = candles.filter((c) => c.time * 1000 >= signal.createdAt.getTime());

  let status: OutcomeStatus = OutcomeStatus.UNKNOWN;
  let resolvedAt: Date | undefined;
  let mfe = 0;
  let mae = 0;

  for (const candle of future) {
    const high = candle.high;
    const low = candle.low;

    if (signal.side === Side.BUY) {
      mfe = Math.max(mfe, (high - signal.entry) / signal.entry);
      mae = Math.min(mae, (low - signal.entry) / signal.entry);
      const tpHit = high >= signal.takeProfit;
      const slHit = low <= signal.stopLoss;
      if (tpHit && slHit) {
        status = OutcomeStatus.UNKNOWN;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
      if (tpHit) {
        status = OutcomeStatus.WIN;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
      if (slHit) {
        status = OutcomeStatus.LOSS;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
    } else {
      mfe = Math.max(mfe, (signal.entry - low) / signal.entry);
      mae = Math.min(mae, (signal.entry - high) / signal.entry);
      const tpHit = low <= signal.takeProfit;
      const slHit = high >= signal.stopLoss;
      if (tpHit && slHit) {
        status = OutcomeStatus.UNKNOWN;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
      if (tpHit) {
        status = OutcomeStatus.WIN;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
      if (slHit) {
        status = OutcomeStatus.LOSS;
        resolvedAt = new Date(candle.time * 1000);
        break;
      }
    }
  }

  if (!resolvedAt && now > outcome.expiryAt) {
    status = OutcomeStatus.EXPIRED;
    resolvedAt = now;
  }

  const risk = Math.abs(signal.entry - signal.stopLoss);
  const reward = Math.abs(signal.takeProfit - signal.entry);
  const rr = risk > 0 ? reward / risk : null;
  const realized = status === OutcomeStatus.WIN ? rr : status === OutcomeStatus.LOSS ? -1 : null;

  await prisma.signalOutcome.update({
    where: { signalId },
    data: { status, resolvedAt, mfe, mae, rMultiple: realized, notes: "Auto-resolved from Binance candle data" }
  });
}

function mapTf(tf: string) {
  return ["1m", "3m", "5m", "15m", "1h", "4h", "1d"].includes(tf) ? tf : "1h";
}
