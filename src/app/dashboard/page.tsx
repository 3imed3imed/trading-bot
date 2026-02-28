"use client";

import { useState } from "react";
import { ChartPanel } from "@/components/ChartPanel";
import { ConsensusCard } from "@/components/ConsensusCard";

export default function DashboardPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [timeframe, setTimeframe] = useState("1h");

  return (
    <main>
      <h2>Dashboard</h2>
      <div className="card">
        <label>Symbol: </label>
        <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          <option>BTCUSDT</option>
          <option>ETHUSDT</option>
          <option>SOLUSDT</option>
        </select>
        <label style={{ marginLeft: 10 }}>Timeframe: </label>
        <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
          <option>1m</option>
          <option>5m</option>
          <option>15m</option>
          <option>1h</option>
          <option>4h</option>
          <option>1d</option>
        </select>
      </div>
      <ChartPanel symbol={symbol} timeframe={timeframe} />
      <ConsensusCard symbol={symbol} timeframe={timeframe} />
    </main>
  );
}
