import fs from "node:fs";
import path from "node:path";

const TEST_DATABASE_NAME = "mealslot_test";

function readEnvFileValue(name: string): string | undefined {
  const envPath = path.resolve(process.cwd(), ".env.local");
  if (!fs.existsSync(envPath)) return undefined;

  const line = fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .find((candidate) => candidate.startsWith(`${name}=`));

  if (!line) return undefined;

  const value = line.slice(name.length + 1).trim();
  const quoted =
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"));

  return quoted ? value.slice(1, -1) : value;
}

export function getTestDatabaseUrl(): string {
  const configuredUrl =
    process.env.TEST_DATABASE_URL ?? readEnvFileValue("DATABASE_URL");

  if (!configuredUrl) {
    throw new Error(
      "Set TEST_DATABASE_URL or configure DATABASE_URL in .env.local before running Playwright.",
    );
  }

  const testUrl = new URL(configuredUrl);
  testUrl.pathname = `/${TEST_DATABASE_NAME}`;

  if (testUrl.pathname !== `/${TEST_DATABASE_NAME}`) {
    throw new Error("Playwright refused to use a non-test database.");
  }

  return testUrl.toString();
}
