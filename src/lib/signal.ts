import crypto from "crypto";
import { Side, VerificationTier } from "@prisma/client";
import { prisma } from "./prisma";

export type NormalizedSignalInput = {
  sourceId: string;
  assetClass: "crypto" | "forex" | "stocks" | "commodities";
  symbol: string;
  timeframe: string;
  side: Side;
  createdAt: Date;
  entry: number;
  stopLoss: number;
  takeProfit: number;
  confidenceRaw: number;
  verificationTier: VerificationTier;
  rawPayload: unknown;
};

const SYMBOL_MAP: Record<string, string> = {
  "BTC/USDT": "BTCUSDT",
  XBTUSD: "BTCUSDT"
};

export function canonicalizeSymbol(symbol: string): string {
  const upper = symbol.toUpperCase().trim();
  const mapped = SYMBOL_MAP[upper];
  if (mapped) return mapped;
  return upper.replace(/[:\-_/]/g, "");
}

export function normalizeTimeframe(tf: string): string {
  const raw = tf.trim();
  const map: Record<string, string> = {
    "60": "1h",
    "240": "4h",
    D: "1d",
    H1: "1h",
    H4: "4h"
  };
  return (map[raw.toUpperCase()] || raw).toLowerCase();
}

export function payloadHash(payload: unknown): string {
  return crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
}

export function deriveExpiry(createdAt: Date, timeframe: string): Date {
  const tf = normalizeTimeframe(timeframe);
  const match = tf.match(/^(\d+)(m|h|d)$/i);
  const multiplier: Record<string, number> = { m: 24, h: 24, d: 10 };

  if (!match) {
    return new Date(createdAt.getTime() + 24 * 60 * 60 * 1000);
  }

  const value = Number(match[1]);
  const unit = match[2].toLowerCase();
  const baseMinutes = unit === "m" ? value : unit === "h" ? value * 60 : value * 24 * 60;
  const totalMinutes = baseMinutes * (multiplier[unit] || 24);
  return new Date(createdAt.getTime() + totalMinutes * 60 * 1000);
}

export async function saveSignal(input: NormalizedSignalInput) {
  const canonicalSymbol = canonicalizeSymbol(input.symbol);
  const timeframe = normalizeTimeframe(input.timeframe);
  const dedupBucket = Math.floor(input.createdAt.getTime() / (5 * 60 * 1000));
  const dedupKey = `${input.sourceId}:${canonicalSymbol}:${timeframe}:${input.side}:${dedupBucket}`;
  const rawPayloadHash = payloadHash(input.rawPayload);

  const existing = await prisma.signal.findFirst({ where: { dedupKey } });

  const signal = await prisma.signal.create({
    data: {
      sourceId: input.sourceId,
      assetClass: input.assetClass,
      symbol: input.symbol,
      canonicalSymbol,
      timeframe,
      side: input.side,
      createdAt: input.createdAt,
      entry: input.entry,
      stopLoss: input.stopLoss,
      takeProfit: input.takeProfit,
      confidenceRaw: input.confidenceRaw,
      verificationTier: input.verificationTier,
      rawPayload: input.rawPayload as never,
      rawPayloadHash,
      dedupKey,
      isDuplicate: Boolean(existing)
    }
  });

  await prisma.signalOutcome.create({ data: { signalId: signal.id, expiryAt: deriveExpiry(input.createdAt, timeframe) } });

  await prisma.ingestionEvent.create({
    data: {
      connector: input.sourceId,
      status: existing ? "DUPLICATE" : "INGESTED",
      dedupKey,
      payloadHash: rawPayloadHash,
      attempts: 1
    }
  });

  return signal;
}
