# P0 Playwright Test Batch

This folder preserves the evidence from Karthik's first P0 automation batch against the unmodified MealSlot application.

- Execution date: 2026-09-01
- Command: `node scripts\\run-playwright.cjs`
- Environment: Chromium, Next.js test server, WebSocket service, and isolated PostgreSQL database `mealslot_test`
- Outcome: 7 tests executed — 6 passed and 1 failed
- Product behavior changes: none

## Contents

- `D3_P0_RAW_OUTPUT.txt`: raw Playwright console output.
- `D3_P0_RESULTS_SNAPSHOT.md`: expected-versus-observed results and failure analysis.
- `last-run.json`: Playwright status metadata.
- `failure-artifacts/TC-UC04-01/test-failed-1.png`: failure screenshot.
- `failure-artifacts/TC-UC04-01/video.webm`: recorded browser run.
- `failure-artifacts/TC-UC04-01/trace.zip`: Playwright trace for interactive inspection.
- `SHA256SUMS.txt`: checksums for the retained binary artifacts.

The failed test is intentionally retained as assignment evidence; it documents current product behavior rather than a product correction.

