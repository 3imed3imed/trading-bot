import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const outcomes = await prisma.signalOutcome.findMany({ include: { signal: true } });
  const byTf: Record<string, { total: number; win: number }> = {};
  for (const o of outcomes) {
    const tf = o.signal.timeframe;
    byTf[tf] = byTf[tf] || { total: 0, win: 0 };
    byTf[tf].total += 1;
    if (o.status === "WIN") byTf[tf].win += 1;
  }
  return NextResponse.json({ byTimeframe: byTf, rr: outcomes.map((o) => o.rMultiple).filter(Boolean) });
}
