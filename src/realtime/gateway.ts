import { createServer } from "http";
import { Server } from "socket.io";
import IORedis from "ioredis";

const port = Number(process.env.REALTIME_PORT || 4001);
const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: "*" }
});

const sub = new IORedis(redisUrl);
sub.subscribe("signal:new", "consensus:update", "price:update");
sub.on("message", (channel, message) => {
  io.emit(channel, JSON.parse(message));
});

io.on("connection", (socket) => {
  socket.emit("system", { status: "connected" });
});

httpServer.listen(port, () => {
  console.log(`Realtime gateway listening on ${port}`);
});
