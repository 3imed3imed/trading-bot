import { VerificationTier } from "@prisma/client";
import { prisma } from "./prisma";

const tierWeight: Record<VerificationTier, number> = { A: 100, B: 70, C: 40 };

export function computeSourceCredibility(input: {
  tier: VerificationTier;
  winRate: number;
  drawdownProxy: number;
  consistency: number;
  historyDays: number;
  avgRR: number;
  frequency: number;
}) {
  const winRateAdj = (Math.min(input.winRate, 0.75) / 0.75) * 100;
  const drawdownAdj = Math.max(0, 100 - input.drawdownProxy * 100);
  const historyAdj = Math.min(100, (input.historyDays / 180) * 100);
  const avgRrAdj = Math.min(100, Math.max(0, input.avgRR * 25));
  const frequencyAdj = Math.min(100, input.frequency * 10);
  return (
    tierWeight[input.tier] * 0.3 +
    winRateAdj * 0.2 +
    drawdownAdj * 0.15 +
    input.consistency * 0.1 +
    historyAdj * 0.1 +
    avgRrAdj * 0.1 +
    frequencyAdj * 0.05
  );
}

export function computeSignalConfidence(params: {
  completeness: number;
  recency: number;
  sourceCred: number;
  spamPenalty: number;
  conflictPenalty: number;
}) {
  return (
    params.completeness * 0.2 +
    params.recency * 0.15 +
    params.sourceCred * 0.35 +
    (100 - params.spamPenalty) * 0.15 +
    (100 - params.conflictPenalty) * 0.15
  );
}

export async function recomputeConsensus(symbol: string, timeframe: string) {
  const signals = await prisma.signal.findMany({
    where: { canonicalSymbol: symbol, timeframe },
    include: { source: true },
    orderBy: { createdAt: "desc" },
    take: 100
  });

  let buyWeight = 0;
  let sellWeight = 0;
  const contributors: Array<{ source: string; side: string; weight: number }> = [];

  const buyCount = signals.filter((s) => s.side === "BUY").length;
  const sellCount = signals.filter((s) => s.side === "SELL").length;
  const conflictPenalty = Math.abs(buyCount - sellCount) <= Math.ceil(signals.length * 0.2) ? 80 : 10;

  for (const s of signals) {
    const completeness = s.entry && s.stopLoss && s.takeProfit ? 100 : 30;
    const ageHours = (Date.now() - s.createdAt.getTime()) / 3600000;
    const recency = Math.max(5, 100 - ageHours * 2);
    const confidence = computeSignalConfidence({
      completeness,
      recency,
      sourceCred: s.source.reliabilityScore || 50,
      spamPenalty: s.isDuplicate ? 80 : 0,
      conflictPenalty
    });

    const w = (confidence * (s.source.reliabilityScore || 50)) / 100;
    if (s.side === "BUY") buyWeight += w;
    else sellWeight += w;

    contributors.push({ source: s.source.name, side: s.side, weight: Number(w.toFixed(2)) });
    await prisma.signal.update({ where: { id: s.id }, data: { confidenceScore: confidence } });
  }

  const total = buyWeight + sellWeight;
  const buyPct = total > 0 ? buyWeight / total : 0.5;
  const label = total < 200 ? "INSUFFICIENT_DATA" : buyPct >= 0.6 ? "BUY_BIAS" : buyPct <= 0.4 ? "SELL_BIAS" : "MIXED";
  const riskLabel = total < 200 ? "HIGH_RISK" : Math.abs(0.5 - buyPct) < 0.1 ? "ELEVATED_RISK" : "MODERATE_RISK";

  await prisma.consensusSnapshot.create({
    data: {
      symbol,
      timeframe,
      buyWeight,
      sellWeight,
      buyPct,
      label,
      riskLabel,
      confidence: Math.min(100, total / 10),
      explainJson: {
        topContributors: contributors.sort((a, b) => b.weight - a.weight).slice(0, 5),
        conflictDetector: conflictPenalty > 50,
        buyCount,
        sellCount
      }
    }
  });
}
