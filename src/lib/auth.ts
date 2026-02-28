import { NextRequest } from "next/server";

export function getRole(req: NextRequest): "ADMIN" | "USER" {
  const role = req.headers.get("x-role");
  return role === "ADMIN" ? "ADMIN" : "USER";
}

export function assertAdmin(req: NextRequest) {
  if (getRole(req) !== "ADMIN") {
    throw new Error("Forbidden: admin required");
  }
}
