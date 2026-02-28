import { redis } from "./redis";

export async function publish(channel: "signal:new" | "consensus:update" | "price:update", payload: unknown) {
  await redis.publish(channel, JSON.stringify(payload));
}
