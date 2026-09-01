# MealSlot Playwright E2E Tests

This directory contains the shared Playwright harness for testing the cloned MealSlot application without changing product behavior. Add new automated cases here and preserve genuine failures as assignment evidence.

## Safety boundary

The E2E setup resets and reseeds a PostgreSQL database before a test run. It refuses to perform that reset unless the database name is exactly `mealslot_test`.

Never point `TEST_DATABASE_URL` at a development, shared, or production database. Do not commit passwords, API keys, `.env.local`, saved authentication state, Playwright reports, or generated test results.

## Prerequisites

- Node.js and pnpm
- PostgreSQL running locally or at a teammate-controlled test host
- An existing, disposable PostgreSQL database named `mealslot_test`
- Ports `3100` and `4101` available during execution

Install project dependencies from `proj2/mealslot`:

```powershell
pnpm install
```

Install Chromium into the cache location used by the local runner:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) ".cache\ms-playwright"
pnpm exec playwright install chromium
```

## Configure the test database

Set `TEST_DATABASE_URL` for the current PowerShell session. Replace the placeholders with local PostgreSQL credentials; never commit the resulting value.

```powershell
$env:TEST_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/mealslot_test?schema=public"
```

If `TEST_DATABASE_URL` is absent, the runner reads `DATABASE_URL` from `.env.local` and changes only its database name to `mealslot_test`. The configured database must use PostgreSQL; the SQLite example in `.env.example` is not suitable for this E2E harness.

## Build and run

Create the production build used by Playwright:

```powershell
pnpm build:e2e
```

Run the complete E2E suite:

```powershell
pnpm test:e2e
```

Useful filtered commands:

```powershell
pnpm test:e2e -- --list
pnpm test:e2e -- --grep "@p0"
pnpm test:e2e -- --grep "@p1"
pnpm test:e2e -- tests/e2e/p0-api.spec.ts
```

The runner starts Next.js at `http://127.0.0.1:3100` and the WebSocket service at `http://127.0.0.1:4101`, then stops both after Playwright finishes.

## Adding team test cases

1. Add or extend a `*.spec.ts` file under `tests/e2e`.
2. Include the traceable test ID in the title, such as `TC-UC03-01`.
3. Add a priority marker such as `@p0`, `@p1`, or `@p2`.
4. Keep test data isolated and deterministic.
5. Test current behavior; do not change application logic merely to make a test pass.
6. Record the expected result and exact observed result in the team's D3 table.

`p0-api.spec.ts` and `p1-api.spec.ts` demonstrate API/database workflows. `smoke.spec.ts` demonstrates a real browser journey, and `p1-realtime.spec.ts` demonstrates isolated multi-browser party workflows.

## Preserving evidence

Playwright writes generated reports to `playwright-report` and artifacts to `test-results`; both are intentionally ignored by Git. For graded evidence, copy only the relevant raw output, screenshot, video, or trace into the appropriate folder under `deliverables/members/<name>/` and explain every failure. Do not commit caches or the entire generated report directory.
