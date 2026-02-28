import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { Side, VerificationTier } from "@prisma/client";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { saveSignal } from "@/lib/signal";
import { publish } from "@/lib/realtime";
import { enqueueOutcome, scoreRecomputeQueue } from "@/lib/queue";
import { checkCircuit, enforceRateLimit, tripCircuit } from "@/lib/resilience";

const schema = z.object({
  sourceId: z.string(),
  symbol: z.string(),
  timeframe: z.string(),
  side: z.enum(["BUY", "SELL"]),
  entry: z.number(),
  stop_loss: z.number(),
  take_profit: z.number(),
  confidence_raw: z.number().min(0).max(100),
  created_at: z.string().optional()
});

function verifyHmac(body: string, signature: string | null) {
  const secret = process.env.TRADINGVIEW_HMAC_SECRET;
  if (!secret) return true;
  if (!signature) return false;
  const digest = crypto.createHmac("sha256", secret).update(body).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signature));
}

export async function POST(req: NextRequest) {
  const rawBody = await req.text();

  try {
    await enforceRateLimit("tradingview", 120, 60);
    await checkCircuit("tradingview");

    const apiKey = req.headers.get("x-api-key");
    const sig = req.headers.get("x-signature");

    const apiOk = process.env.TRADINGVIEW_API_KEY ? apiKey === process.env.TRADINGVIEW_API_KEY : true;
    const hmacOk = verifyHmac(rawBody, sig);
    if (!apiOk || !hmacOk) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const payload = schema.parse(JSON.parse(rawBody));
    const signal = await saveSignal({
      sourceId: payload.sourceId,
      assetClass: "crypto",
      symbol: payload.symbol,
      timeframe: payload.timeframe,
      side: payload.side as Side,
      createdAt: payload.created_at ? new Date(payload.created_at) : new Date(),
      entry: payload.entry,
      stopLoss: payload.stop_loss,
      takeProfit: payload.take_profit,
      confidenceRaw: payload.confidence_raw,
      verificationTier: VerificationTier.B,
      rawPayload: payload
    });

    await enqueueOutcome(signal.id);
    await scoreRecomputeQueue.add("recompute", { symbol: signal.canonicalSymbol, timeframe: signal.timeframe });
    await publish("signal:new", signal);

    await prisma.auditLog.create({ data: { actor: "tradingview", eventType: "INGEST_SUCCESS", payload } });
    return NextResponse.json({ ok: true, id: signal.id, duplicate: signal.isDuplicate });
  } catch (error) {
    await tripCircuit("tradingview", 20);
    await prisma.auditLog.create({
      data: {
        actor: "tradingview",
        eventType: "INGEST_FAILURE",
        payload: { message: (error as Error).message, body: rawBody.slice(0, 1000) }
      }
    });

    return NextResponse.json({ error: (error as Error).message }, { status: 400 });
  }
}
