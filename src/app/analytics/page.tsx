"use client";
import useSWR from "swr";
const fetcher = (u: string) => fetch(u).then((r) => r.json());

export default function AnalyticsPage() {
  const { data } = useSWR("/api/analytics", fetcher, { refreshInterval: 30000 });
  return (
    <main>
      <h2>Analytics</h2>
      <div className="card"><h3>Win Rate by Timeframe</h3><pre>{JSON.stringify(data?.byTimeframe, null, 2)}</pre></div>
      <div className="card"><h3>RR Distribution</h3><pre>{JSON.stringify(data?.rr?.slice(0, 100), null, 2)}</pre></div>
    </main>
  );
}
