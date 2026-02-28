"use client";

import { createChart, ISeriesApi, CandlestickData } from "lightweight-charts";
import { useEffect, useRef } from "react";
import useSWR from "swr";

const fetcher = (u: string) => fetch(u).then((r) => r.json());

export function ChartPanel({ symbol, timeframe }: { symbol: string; timeframe: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const { data } = useSWR(`/api/market/candles?symbol=${symbol}&timeframe=${timeframe}`, fetcher, { refreshInterval: 15000 });

  useEffect(() => {
    if (!ref.current || seriesRef.current) return;
    const chart = createChart(ref.current, { width: 900, height: 360, layout: { background: { color: "#0d1117" }, textColor: "#e6edf3" } });
    seriesRef.current = chart.addCandlestickSeries();
    return () => chart.remove();
  }, []);

  useEffect(() => {
    if (!data?.candles || !seriesRef.current) return;
    const candles: CandlestickData[] = data.candles.map((c: any) => ({
      time: c.time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close
    }));
    seriesRef.current.setData(candles);
  }, [data]);

  return <div ref={ref} />;
}
