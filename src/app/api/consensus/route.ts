import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  const symbol = req.nextUrl.searchParams.get("symbol") || "BTCUSDT";
  const timeframe = req.nextUrl.searchParams.get("timeframe") || "1h";
  const latest = await prisma.consensusSnapshot.findFirst({
    where: { symbol, timeframe },
    orderBy: { createdAt: "desc" }
  });
  return NextResponse.json(latest);
}
