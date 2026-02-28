import { Queue } from "bullmq";
import { redis } from "./redis";

const connection = redis.duplicate();

export const ingestionRetryQueue = new Queue("ingestion-retry", { connection });
export const outcomeResolveQueue = new Queue("outcome-resolve", { connection });
export const scoreRecomputeQueue = new Queue("score-recompute", { connection });
export const marketSyncQueue = new Queue("market-sync", { connection });

export async function enqueueOutcome(signalId: string) {
  await outcomeResolveQueue.add(
    "resolve",
    { signalId },
    {
      attempts: 5,
      backoff: { type: "exponential", delay: 2000 }
    }
  );
}
