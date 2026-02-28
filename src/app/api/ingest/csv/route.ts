import { NextRequest, NextResponse } from "next/server";
import { parse } from "csv-parse/sync";
import { Side, VerificationTier } from "@prisma/client";
import { z } from "zod";
import { saveSignal } from "@/lib/signal";

const rowSchema = z.object({
  assetClass: z.enum(["crypto", "forex", "stocks", "commodities"]).default("crypto"),
  symbol: z.string().min(3),
  timeframe: z.string().min(1),
  side: z.enum(["BUY", "SELL"]),
  created_at: z.string().optional(),
  entry: z.coerce.number(),
  stop_loss: z.coerce.number(),
  take_profit: z.coerce.number(),
  confidence_raw: z.coerce.number().min(0).max(100).default(50),
  verification_tier: z.enum(["A", "B", "C"]).default("C")
});

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const file = form.get("file") as File | null;
  const sourceId = String(form.get("sourceId") || "");

  if (!file) return NextResponse.json({ error: "Missing file" }, { status: 400 });
  if (!sourceId) return NextResponse.json({ error: "Missing sourceId" }, { status: 400 });

  const text = await file.text();
  const records = parse(text, { columns: true, skip_empty_lines: true, trim: true }) as Record<string, string>[];

  const ids: string[] = [];
  const errors: Array<{ row: number; error: string }> = [];

  for (const [idx, rec] of records.entries()) {
    const parsed = rowSchema.safeParse({
      ...rec,
      side: rec.side?.toUpperCase(),
      verification_tier: rec.verification_tier?.toUpperCase()
    });

    if (!parsed.success) {
      errors.push({ row: idx + 1, error: parsed.error.issues.map((i) => i.message).join(", ") });
      continue;
    }

    const r = parsed.data;
    const signal = await saveSignal({
      sourceId,
      assetClass: r.assetClass,
      symbol: r.symbol,
      timeframe: r.timeframe,
      side: r.side as Side,
      createdAt: r.created_at ? new Date(r.created_at) : new Date(),
      entry: r.entry,
      stopLoss: r.stop_loss,
      takeProfit: r.take_profit,
      confidenceRaw: r.confidence_raw,
      verificationTier: r.verification_tier as VerificationTier,
      rawPayload: rec
    });

    ids.push(signal.id);
  }

  return NextResponse.json({ ok: true, ingested: ids.length, ids, errors });
}
