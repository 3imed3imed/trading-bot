import { NextRequest, NextResponse } from "next/server";
import { Side, VerificationTier } from "@prisma/client";
import { prisma } from "@/lib/prisma";
import { saveSignal } from "@/lib/signal";
import { enqueueOutcome } from "@/lib/queue";
import { publish } from "@/lib/realtime";

function parseTelegramSignal(text: string) {
  const pattern = /(BUY|SELL)\s+([A-Z0-9\/]+)\s+(\d+[mhd])\s+ENTRY\s*[:=]\s*([\d.]+)\s+SL\s*[:=]\s*([\d.]+)\s+TP\s*[:=]\s*([\d.]+)/i;
  const match = text.match(pattern);
  if (!match) return null;
  return {
    side: match[1].toUpperCase() as Side,
    symbol: match[2],
    timeframe: match[3],
    entry: Number(match[4]),
    stopLoss: Number(match[5]),
    takeProfit: Number(match[6])
  };
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const msgText = body?.message?.text || body?.text || "";
  const parsed = parseTelegramSignal(msgText);
  if (!parsed) return NextResponse.json({ error: "Pattern not matched" }, { status: 422 });

  const sourceId = body.sourceId;
  const signal = await saveSignal({
    sourceId,
    assetClass: "crypto",
    symbol: parsed.symbol,
    timeframe: parsed.timeframe,
    side: parsed.side,
    createdAt: new Date(),
    entry: parsed.entry,
    stopLoss: parsed.stopLoss,
    takeProfit: parsed.takeProfit,
    confidenceRaw: 55,
    verificationTier: VerificationTier.C,
    rawPayload: {
      telegramMessageId: body?.message?.message_id,
      chat: body?.message?.chat,
      forwardedFrom: body?.message?.forward_from_chat,
      text: msgText
    }
  });
  await enqueueOutcome(signal.id);
  await publish("signal:new", signal);
  await prisma.auditLog.create({ data: { actor: "telegram", eventType: "INGEST_SUCCESS", payload: body } });

  return NextResponse.json({ ok: true, id: signal.id });
}
