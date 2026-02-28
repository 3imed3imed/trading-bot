import { PrismaClient, ConnectorStatus, VerificationTier } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.source.createMany({
    data: [
      {
        name: "TradingView Webhook",
        sourceType: "TRADINGVIEW",
        verificationTier: VerificationTier.B,
        connectorStatus: ConnectorStatus.SUPPORTED,
        connectorReason: "Webhook ingest with API key/HMAC validation"
      },
      {
        name: "Telegram Forward",
        sourceType: "TELEGRAM",
        verificationTier: VerificationTier.C,
        connectorStatus: ConnectorStatus.SUPPORTED,
        connectorReason: "Forwarded messages only; no scraping"
      },
      {
        name: "Myfxbook",
        sourceType: "MYFXBOOK",
        verificationTier: VerificationTier.B,
        connectorStatus: ConnectorStatus.PARTIAL,
        connectorReason: "Official integrations/exports only"
      },
      {
        name: "Unsupported Copy Platform",
        sourceType: "COPY_PLATFORM",
        verificationTier: VerificationTier.C,
        connectorStatus: ConnectorStatus.NOT_AVAILABLE,
        connectorReason: "No official API/permission"
      }
    ],
    skipDuplicates: true
  });
}

main().finally(async () => {
  await prisma.$disconnect();
});
