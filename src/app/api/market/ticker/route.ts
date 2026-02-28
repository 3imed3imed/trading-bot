import { NextRequest, NextResponse } from "next/server";
import { fetchBinanceTicker } from "@/lib/market";
import { publish } from "@/lib/realtime";

export async function GET(req: NextRequest) {
  const symbol = req.nextUrl.searchParams.get("symbol") || "BTCUSDT";
  const ticker = await fetchBinanceTicker(symbol);
  await publish("price:update", ticker);
  return NextResponse.json(ticker);
}
