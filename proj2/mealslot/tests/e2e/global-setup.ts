import { execFileSync } from "node:child_process";
import path from "node:path";

import { PrismaClient } from "@prisma/client";

import { getTestDatabaseUrl } from "./test-env";

export default async function globalSetup() {
  const databaseUrl = getTestDatabaseUrl();
  const parsedUrl = new URL(databaseUrl);

  if (parsedUrl.pathname !== "/mealslot_test") {
    throw new Error("Database reset is allowed only for mealslot_test.");
  }

  const prismaCli = path.resolve(
    process.cwd(),
    "node_modules/prisma/build/index.js",
  );
  const commandEnvironment = {
    ...process.env,
    DATABASE_URL: databaseUrl,
  };

  execFileSync(
    process.execPath,
    [prismaCli, "db", "push", "--skip-generate"],
    {
      cwd: process.cwd(),
      env: commandEnvironment,
      stdio: "inherit",
    },
  );

  const prisma = new PrismaClient({
    datasources: {
      db: { url: databaseUrl },
    },
  });

  try {
    await prisma.favorite.deleteMany();
    await prisma.partyMember.deleteMany();
    await prisma.spin.deleteMany();
    await prisma.party.deleteMany();
    await prisma.user.deleteMany();
    await prisma.dish.deleteMany();
  } finally {
    await prisma.$disconnect();
  }

  execFileSync(process.execPath, [prismaCli, "db", "seed"], {
    cwd: process.cwd(),
    env: commandEnvironment,
    stdio: "inherit",
  });
}
