import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  const symbol = req.nextUrl.searchParams.get("symbol") || undefined;
  const timeframe = req.nextUrl.searchParams.get("timeframe") || undefined;
  const sourceId = req.nextUrl.searchParams.get("sourceId") || undefined;
  const signals = await prisma.signal.findMany({
    where: { canonicalSymbol: symbol, timeframe, sourceId },
    include: { source: true, outcomes: true },
    orderBy: { createdAt: "desc" },
    take: 200
  });
  return NextResponse.json(signals);
}
