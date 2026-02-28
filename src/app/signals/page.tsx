"use client";
import useSWR from "swr";

const fetcher = (u: string) => fetch(u).then((r) => r.json());

export default function SignalsPage() {
  const { data } = useSWR("/api/signals", fetcher, { refreshInterval: 5000 });
  return (
    <main>
      <h2>Signals Feed</h2>
      <div className="card">
        <table>
          <thead><tr><th>Time</th><th>Symbol</th><th>TF</th><th>Side</th><th>Source</th><th>Outcome</th></tr></thead>
          <tbody>
            {data?.map((s: any) => (
              <tr key={s.id}>
                <td>{new Date(s.createdAt).toLocaleString()}</td><td>{s.canonicalSymbol}</td><td>{s.timeframe}</td><td>{s.side}</td><td>{s.source.name}</td><td>{s.outcomes?.[0]?.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
