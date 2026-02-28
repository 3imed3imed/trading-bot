"use client";
import useSWR from "swr";

const fetcher = (u: string) => fetch(u).then((r) => r.json());

export function ConsensusCard({ symbol, timeframe }: { symbol: string; timeframe: string }) {
  const { data } = useSWR(`/api/consensus?symbol=${symbol}&timeframe=${timeframe}`, fetcher, { refreshInterval: 5000 });

  return (
    <div className="card">
      <h3>Consensus</h3>
      {data ? (
        <>
          <p>
            <span className="badge">{data.label}</span> Risk: <strong>{data.riskLabel}</strong> Confidence: {data.confidence?.toFixed?.(2)}
          </p>
          <p>buyWeight={data.buyWeight?.toFixed?.(2)} sellWeight={data.sellWeight?.toFixed?.(2)} buyPct={(data.buyPct * 100)?.toFixed?.(1)}%</p>
          <details>
            <summary>Why this consensus?</summary>
            <pre>{JSON.stringify(data.explainJson, null, 2)}</pre>
          </details>
          <p className="disclaimer">Consensus is informational only, not guaranteed profit or financial advice.</p>
        </>
      ) : (
        <p>Waiting for enough data…</p>
      )}
    </div>
  );
}
