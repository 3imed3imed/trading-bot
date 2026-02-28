import { redis } from "./redis";

export async function enforceRateLimit(key: string, limit: number, windowSec: number) {
  const redisKey = `rl:${key}`;
  const count = await redis.incr(redisKey);
  if (count === 1) await redis.expire(redisKey, windowSec);
  if (count > limit) throw new Error("Rate limit exceeded");
}

export async function checkCircuit(connector: string) {
  const state = await redis.get(`cb:${connector}`);
  if (state === "open") throw new Error(`Circuit open for ${connector}`);
}

export async function tripCircuit(connector: string, ttlSec = 60) {
  await redis.set(`cb:${connector}`, "open", "EX", ttlSec);
}
