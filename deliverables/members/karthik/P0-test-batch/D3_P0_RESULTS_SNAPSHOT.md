# MealSlot D3 — P0 Automation Results Snapshot

**Status:** First automation batch  
**Command:** `node scripts\run-playwright.cjs`  
**Environment:** Chromium; Next.js on `127.0.0.1:3100`; WebSocket service on `127.0.0.1:4101`; isolated PostgreSQL database `mealslot_test`; 59 seeded dishes  
**Product behavior changes:** None  
**Summary:** 7 executed — 6 PASS, 1 FAIL, 0 BLOCKED

## Results

| Test | Why we tried it | Expected | What happened | Result | Evidence / explanation |
|---|---|---|---|---|---|
| `TC-UC04-01` | UC04 main flow says valid default reel categories produce three displayed meal suggestions. | Default Breakfast, Lunch, and Dinner spin displays three real dishes and no `No options` placeholder. | Selected Dishes appeared, but Playwright found six visible/text occurrences of `No options`; screenshot shows all three reels as placeholders. | **FAIL** | Screenshot, video, and trace retained under `test-results/smoke-TC-UC04-01-p0-completes-the-default-solo-spin-chromium/`. Likely product defect: UI submits title-case category names while seeded database categories are lowercase and the backend lookup is case-sensitive. |
| `TC-UC04-02` | UC04 extensions require missing categories to be rejected and an empty candidate category to return a placeholder. | Missing configuration returns 400; empty category returns one harmless `No options` result. | Both variants matched the expected status and response shape. | PASS | Raw Playwright list output; API assertions. |
| `TC-UC09-01` | Allergen exclusion is safety-critical. | A dinner spin excluding fish contains no fish in any candidate reel or selected result. | Three non-placeholder selections returned; no candidate or selected allergen list contained fish. | PASS | Raw Playwright output; response assertions cover reels and selection. |
| `TC-UC16-01` | UC16 requires a unique active party and creator membership. | Six-character code, active party, one creator member with supplied nickname. | API and party-state response matched all expectations. | PASS | Raw Playwright output; create/state assertions. |
| `TC-UC17-01` | UC17 requires successful membership creation and shared state visibility. | Join response identifies the same party; state lists host and new member once each. | Party state contained exactly the two expected memberships and nicknames. | PASS | Raw Playwright output; join/state assertions. |
| `TC-UC02-01` | UC02 defines strictest diet, allergen union, and minimum budget/time merge rules. | Vegetarian plus vegan merges to vegan; allergens union; budget/time use minima; stored constraints match response. | Returned and subsequently fetched constraints matched the expected merge. | PASS | Raw Playwright output; update/state assertions. |
| `TC-UC14-01` | UC14 requires only the departing membership to be removed while the party remains active. | Joined member disappears; creator remains; party stays active. | State contained only the creator and `isActive: true`. | PASS | Raw Playwright output; leave/state assertions. |

## Failure analysis: TC-UC04-01

The failure is reproducible evidence of current behavior, not a test setup failure:

1. The browser initializes categories as `Breakfast`, `Lunch`, and `Dinner` and sends those strings in the spin request (`app/(site)/page.tsx`).
2. Seed data stores category values as lowercase `breakfast`, `lunch`, and `dinner` (`prisma/seed.ts`).
3. Dish lookup applies an exact category condition (`lib/dishes.ts`).
4. The direct API safety test passes when it deliberately sends lowercase `dinner`, while the real default UI journey returns placeholders.

This explains the API/UI contrast without changing the cloned product. It should be reported as a product defect or use-case/code mismatch and shown as the required genuine failure in the demo video.

## Next automation batch

1. `TC-UC03-01` and `TC-UC03-03`: keep quorum and vote replacement with multiple contexts.
2. `TC-UC04-03`: verify allergen safety of the party hardcoded fallback.
3. `TC-UC08-01`, `TC-UC12-01`, and `TC-UC13-01`: authenticated favorite persistence lifecycle.
4. `TC-UC16-02`, `TC-UC17-02`, and `TC-UC14-03`: party validation/failure paths.
5. `TC-UC20-01` and `TC-UC20-03`: chat delivery through WebSocket and same-origin fallback.


