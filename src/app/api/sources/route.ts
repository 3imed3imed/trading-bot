import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const sources = await prisma.source.findMany({ orderBy: { reliabilityScore: "desc" } });
  return NextResponse.json(sources);
}
