import { NextRequest, NextResponse } from "next/server";
import { Side, VerificationTier } from "@prisma/client";
import { saveSignal } from "@/lib/signal";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const signal = await saveSignal({
    sourceId: body.sourceId,
    assetClass: body.assetClass || "crypto",
    symbol: body.symbol,
    timeframe: body.timeframe,
    side: body.side as Side,
    createdAt: body.createdAt ? new Date(body.createdAt) : new Date(),
    entry: Number(body.entry),
    stopLoss: Number(body.stopLoss),
    takeProfit: Number(body.takeProfit),
    confidenceRaw: Number(body.confidenceRaw || 50),
    verificationTier: (body.verificationTier || "C") as VerificationTier,
    rawPayload: body
  });

  return NextResponse.json({ ok: true, id: signal.id });
}
