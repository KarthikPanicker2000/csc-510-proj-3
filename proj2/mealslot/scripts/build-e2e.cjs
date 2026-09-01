const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const projectRoot = process.cwd();
const trackedBuildFiles = [
  "next.config.js",
  "next-env.d.ts",
  "tsconfig.json",
  "tsconfig.tsbuildinfo",
];
const snapshots = new Map();

function readLocalDatabaseUrl() {
  if (process.env.TEST_DATABASE_URL) return process.env.TEST_DATABASE_URL;

  const envPath = path.resolve(projectRoot, ".env.local");
  const line = fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .find((candidate) => candidate.startsWith("DATABASE_URL="));

  if (!line) throw new Error("DATABASE_URL is missing from .env.local.");

  const value = line.slice("DATABASE_URL=".length).trim();
  const quoted =
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"));
  return quoted ? value.slice(1, -1) : value;
}

function getTestDatabaseUrl() {
  const url = new URL(readLocalDatabaseUrl());
  url.pathname = "/mealslot_test";
  if (url.pathname !== "/mealslot_test") {
    throw new Error("E2E build refused to use a non-test database.");
  }
  return url.toString();
}

function snapshotTrackedBuildFiles() {
  for (const relativePath of trackedBuildFiles) {
    const absolutePath = path.resolve(projectRoot, relativePath);
    snapshots.set(
      absolutePath,
      fs.existsSync(absolutePath) ? fs.readFileSync(absolutePath) : null,
    );
  }
}

function restoreTrackedBuildFiles() {
  for (const [absolutePath, contents] of snapshots) {
    if (contents === null) {
      if (fs.existsSync(absolutePath)) fs.rmSync(absolutePath);
    } else {
      fs.writeFileSync(absolutePath, contents);
    }
  }
}

function constrainNextBuildRoot() {
  const configPath = path.resolve(projectRoot, "next.config.js");
  const config = fs.readFileSync(configPath, "utf8");
  if (config.includes("outputFileTracingRoot:")) return;

  const marker = "const nextConfig = {";
  if (!config.includes(marker)) {
    throw new Error("Unable to apply the temporary E2E tracing root.");
  }

  fs.writeFileSync(
    configPath,
    config.replace(marker, `${marker}\n  outputFileTracingRoot: __dirname,`),
  );
}

function runNodeModule(modulePath, args, environment) {
  const result = spawnSync(process.execPath, [modulePath, ...args], {
    cwd: projectRoot,
    env: environment,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exitCode = result.status ?? 1;
  return result.status === 0;
}

snapshotTrackedBuildFiles();

try {
  constrainNextBuildRoot();

  const environment = {
    ...process.env,
    DATABASE_URL: getTestDatabaseUrl(),
    NEXT_PUBLIC_WS_URL: "http://127.0.0.1:4101",
  };
  const prismaCli = require.resolve("prisma/build/index.js");
  const nextCli = require.resolve("next/dist/bin/next");

  const generated = runNodeModule(prismaCli, ["generate"], environment);
  if (generated) runNodeModule(nextCli, ["build", "--webpack"], environment);
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
} finally {
  restoreTrackedBuildFiles();
}
