import { NextRequest, NextResponse } from "next/server";
import { fetchBinanceCandles } from "@/lib/market";

export async function GET(req: NextRequest) {
  const symbol = req.nextUrl.searchParams.get("symbol") || "BTCUSDT";
  const interval = req.nextUrl.searchParams.get("timeframe") || "1h";
  const candles = await fetchBinanceCandles(symbol, interval, 500);
  return NextResponse.json({ symbol, interval, candles });
}
