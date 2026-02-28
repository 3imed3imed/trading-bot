export type Candle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export async function fetchBinanceCandles(symbol: string, interval: string, limit = 500): Promise<Candle[]> {
  const url = new URL("https://api.binance.com/api/v3/klines");
  url.searchParams.set("symbol", symbol);
  url.searchParams.set("interval", interval);
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url, { next: { revalidate: 10 } });
  if (!res.ok) throw new Error(`Failed to fetch klines: ${res.status}`);

  const raw = (await res.json()) as [number, string, string, string, string, string][];
  return raw.map((k) => ({
    time: Math.floor(k[0] / 1000),
    open: Number(k[1]),
    high: Number(k[2]),
    low: Number(k[3]),
    close: Number(k[4]),
    volume: Number(k[5])
  }));
}

export async function fetchBinanceTicker(symbol: string): Promise<{ symbol: string; price: number }> {
  const url = new URL("https://api.binance.com/api/v3/ticker/price");
  url.searchParams.set("symbol", symbol);
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch ticker");
  const data = (await res.json()) as { symbol: string; price: string };
  return { symbol: data.symbol, price: Number(data.price) };
}
