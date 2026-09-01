const fs = require("node:fs");
const http = require("node:http");
const net = require("node:net");
const path = require("node:path");
const { spawn, spawnSync } = require("node:child_process");

const projectRoot = process.cwd();
const cli = require.resolve("@playwright/test/cli");
const nextCli = require.resolve("next/dist/bin/next");
const wsServer = path.resolve(projectRoot, "ws-server", "server.js");
const playwrightArguments = process.argv.slice(2);
const children = [];

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
    throw new Error("Playwright refused to use a non-test database.");
  }
  return url.toString();
}

function isPortOpen(port) {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: "127.0.0.1", port });
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("error", () => resolve(false));
    socket.setTimeout(500, () => {
      socket.destroy();
      resolve(false);
    });
  });
}

function waitForUrl(url, child, timeoutMs) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    let childExited = false;
    child.once("exit", (code) => {
      childExited = true;
      reject(new Error(`${url} server exited early with code ${code}.`));
    });

    const poll = () => {
      if (childExited) return;
      if (Date.now() - startedAt > timeoutMs) {
        reject(new Error(`Timed out waiting for ${url}.`));
        return;
      }

      const request = http.get(url, (response) => {
        response.resume();
        resolve();
      });
      request.on("error", () => setTimeout(poll, 250));
      request.setTimeout(1_000, () => {
        request.destroy();
        setTimeout(poll, 250);
      });
    };

    poll();
  });
}

function stopChild(child) {
  if (!child?.pid) return;
  child.kill("SIGKILL");
}

async function main() {
  const environment = { ...process.env };

  if (!environment.CI && !environment.PLAYWRIGHT_BROWSERS_PATH) {
    environment.PLAYWRIGHT_BROWSERS_PATH = path.resolve(
      projectRoot,
      ".cache",
      "ms-playwright",
    );
  }

  const onlyListsTests = playwrightArguments.includes("--list");
  if (!onlyListsTests) {
    const occupiedPorts = [];
    if (await isPortOpen(3100)) occupiedPorts.push(3100);
    if (await isPortOpen(4101)) occupiedPorts.push(4101);
    if (occupiedPorts.length) {
      throw new Error(
        `Playwright requires free test ports: ${occupiedPorts.join(", ")}.`,
      );
    }

    const testDatabaseUrl = getTestDatabaseUrl();
    const buildId = path.resolve(projectRoot, ".next", "BUILD_ID");
    if (!fs.existsSync(buildId)) {
      throw new Error(
        "No production build found. Run pnpm build:e2e before pnpm test:e2e.",
      );
    }
    const app = spawn(
      process.execPath,
      [nextCli, "start", "--port", "3100"],
      {
        cwd: projectRoot,
        env: {
          ...environment,
          DATABASE_URL: testDatabaseUrl,
          NEXT_PUBLIC_WS_URL: "http://127.0.0.1:4101",
        },
        stdio: "inherit",
      },
    );
    const realtime = spawn(process.execPath, [wsServer], {
      cwd: projectRoot,
      env: { ...environment, PORT: "4101" },
      stdio: "inherit",
    });

    children.push(app, realtime);
    await Promise.all([
      waitForUrl("http://127.0.0.1:3100", app, 30_000),
      waitForUrl("http://127.0.0.1:4101", realtime, 30_000),
    ]);
  }

  const result = spawnSync(
    process.execPath,
    [cli, "test", ...playwrightArguments],
    {
      cwd: projectRoot,
      env: environment,
      stdio: "inherit",
    },
  );

  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
}

main()
  .catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  })
  .finally(() => {
    for (const child of children) stopChild(child);
  });
