import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const sources = await prisma.source.findMany({
    select: { name: true, sourceType: true, connectorStatus: true, connectorReason: true }
  });
  return NextResponse.json(sources);
}
