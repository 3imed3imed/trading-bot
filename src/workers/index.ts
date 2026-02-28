import { Worker } from "bullmq";
import { redis } from "@/lib/redis";
import { resolveSignalOutcome } from "@/lib/outcome";
import { recomputeConsensus, computeSourceCredibility } from "@/lib/scoring";
import { prisma } from "@/lib/prisma";
import { publish } from "@/lib/realtime";

const connection = redis.duplicate();

new Worker(
  "outcome-resolve",
  async (job) => {
    await resolveSignalOutcome(job.data.signalId);
  },
  { connection }
);

new Worker(
  "score-recompute",
  async (job) => {
    const { symbol, timeframe } = job.data as { symbol: string; timeframe: string };
    await recomputeAllSourceScores();
    await recomputeConsensus(symbol, timeframe);
    const latest = await prisma.consensusSnapshot.findFirst({ where: { symbol, timeframe }, orderBy: { createdAt: "desc" } });
    if (latest) await publish("consensus:update", latest);
  },
  { connection }
);

async function recomputeAllSourceScores() {
  const sources = await prisma.source.findMany({ include: { signals: { include: { outcomes: true } } } });
  for (const source of sources) {
    const outcomes = source.signals.flatMap((s) => s.outcomes);
    const settled = outcomes.filter((o) => ["WIN", "LOSS"].includes(o.status));
    const wins = settled.filter((o) => o.status === "WIN").length;
    const winRate = settled.length ? wins / settled.length : 0;
    const avgRR = settled.length ? settled.reduce((a, o) => a + (o.rMultiple || 0), 0) / settled.length : 0;
    const dd = Math.abs(Math.min(0, ...settled.map((o) => o.mae || 0)));
    const score = computeSourceCredibility({
      tier: source.verificationTier,
      winRate,
      drawdownProxy: dd,
      consistency: 60,
      historyDays: Math.max(1, Math.floor((Date.now() - source.createdAt.getTime()) / 86400000)),
      avgRR,
      frequency: source.signals.length / 30
    });

    await prisma.source.update({
      where: { id: source.id },
      data: {
        winRate,
        avgRr: avgRR,
        drawdownProxy: dd,
        signalFrequency: source.signals.length / 30,
        reliabilityScore: score,
        historyDays: Math.max(1, Math.floor((Date.now() - source.createdAt.getTime()) / 86400000)),
        lastActivity: source.signals[0]?.createdAt
      }
    });
  }
}

console.log("Workers started");
