"use client";
import useSWR from "swr";
const fetcher = (u: string) => fetch(u).then((r) => r.json());

export default function SourcesPage() {
  const { data } = useSWR("/api/sources", fetcher, { refreshInterval: 10000 });
  return (
    <main>
      <h2>Sources</h2>
      <table>
        <thead><tr><th>Name</th><th>Tier</th><th>History</th><th>Win Rate</th><th>Drawdown Proxy</th><th>Frequency</th><th>Last Activity</th><th>Reliability</th></tr></thead>
        <tbody>
          {data?.map((s: any) => <tr key={s.id}><td>{s.name}</td><td>{s.verificationTier}</td><td>{s.historyDays}</td><td>{(s.winRate*100).toFixed(1)}%</td><td>{s.drawdownProxy}</td><td>{s.signalFrequency}</td><td>{s.lastActivity ? new Date(s.lastActivity).toLocaleString() : '-'}</td><td>{s.reliabilityScore.toFixed(1)}</td></tr>)}
        </tbody>
      </table>
    </main>
  );
}
