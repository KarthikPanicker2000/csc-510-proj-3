# P1 Playwright Test Batch

This folder preserves evidence from Karthik's second automation batch against the unmodified MealSlot application.

- Execution date: 2026-09-01
- Command: `node scripts\run-playwright.cjs --grep '@p1'`
- Environment: Chromium, Next.js test server, WebSocket service, and isolated PostgreSQL database `mealslot_test`
- Outcome: 11 tests registered — 6 passed, 3 failed, and 2 blocked/skipped
- Product behavior changes: none

## Contents

- `D3_P1_RAW_OUTPUT.txt`: retained Playwright console output from the final run.
- `D3_P1_RESULTS_SNAPSHOT.md`: expected-versus-observed results and defect analysis.
- `last-run.json`: Playwright status metadata.
- `failure-artifacts/TC-UC16-02/trace.zip`: trace for nickname validation failure.
- `failure-artifacts/TC-UC03-01/`: three browser screenshots and a trace for quorum synchronization failure.
- `failure-artifacts/TC-UC20-01/`: two browser screenshots and a trace for chat delivery failure.
- `SHA256SUMS.txt`: checksums for all retained binary artifacts.

Failures and blocked cases are intentionally retained as assignment evidence. The batch tests the repository's current behavior without correcting the product.
