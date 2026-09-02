# Prompt Notes: Model Evaluation on MealSlot (Gemini 3.6 Flash v2)

## Executive Summary & Model Configuration

The 15 prompts in [prompts.md](prompts.md) were evaluated against the MealSlot codebase (`proj2/mealslot`) using **Gemini 3.6 Flash (Medium)**. Per the two distinct rules established for this evaluation:

1. **Prompts 1–5 and 9–15 (Static Context Rule)**: Evaluated using **ONLY** the text pasted inside `prompts.md` itself. No external codebase tools, file viewers, or repository searches were used beyond the pasted content (reusing earlier pasted code sections for prompts 4, 10, 12, and 15 as directed).
2. **Prompts 6, 7, and 8 (Live Execution Rule)**: Executed live in the actual project environment:
   - Installed `pnpm@10.24.0` globally (`npm install -g pnpm@10.24.0`) and verified shell PATH resolution.
   - Installed project dependencies from `proj2/mealslot` via `pnpm install --frozen-lockfile --node-linker=hoisted` (avoiding exFAT symlink `ERR_PNPM_EISDIR` errors).
   - Executed `pnpm typecheck` (0 errors).
   - Wrote unit tests for `lib/scoring.ts` (`weightedSpin`) in `tests/lib/scoring.test.ts` for Prompt 7, executed them (`npx vitest run tests/lib/scoring.test.ts`), and confirmed all 3 tests passed cleanly.
   - Executed `pnpm test` across the full test suite, capturing complete output (**87 test files, 498 total tests: 482 passed, 15 failed, 1 skipped**).
   - Re-ran failing test files standalone to confirm determinism.
   - Executed `pnpm build` (completed successfully in 7.5s with static page generation 17/17).

---

## 1. Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| **1: First contact with repo** | Earned Keep | Mapped the Next.js 16 App Router architecture (`app/`, no `src/` root), Prisma schema (`prisma/schema.prisma`), Socket.IO WebSocket server (`ws-server/`), Vitest test suite, and `@stackframe/stack` integration. Correctly noted README contradictions (README claims Next.js 15, SQLite default, and "Add login system" roadmap item; code uses Next.js 16, Postgres schema provider, and active `@stackframe/stack` auth). |
| **2: Module to user goals** | Earned Keep | Reverse-engineered `lib/rateLimit.ts` to identify the user goal of preventing spin request abuse via a token-bucket rate limiter (CAP=20 tokens, REFILL_MS=60,000). Identified actor, trigger, 5-step main flow, line citation (`lib/rateLimit.ts:423-428` for 429 response handling), and confirmed zero dead code in the module. |
| **3: Use case + edges** | Earned Keep | Structured canonical UC7 (**View Recipe Videos for a Dish**) in standard table format from `app/api/videos/route.ts`. Cited 3 handled extensions (`app/api/videos/route.ts:521-526` for Zod validation, `566-592` for missing API key fallback, `554-560` for per-dish error catching). Highlighted 3 unhandled extensions (generic Zod error on malformed JSON, silent empty result on 200 OK quota errors, unconstrained dish query string length). |
| **4: Undocumented product features** | Earned Keep | Identified 4 features in code omitted from README: (1) In-memory token-bucket rate limiter (`lib/rateLimit.ts:406-434`); (2) Active `@stackframe/stack` auth integration (`app/handler/[...stack]/page.tsx`); (3) Full CRUD API for dish management (`app/api/dishes/route.ts`, `app/api/dishes/[id]/route.ts`); (4) 10-second time-bucket seeded PRNG (`lib/rng.ts:134-160`). |
| **5: Rotten / fragile areas** | Earned Keep | Evaluated `git log --stat` churn data and identified top fragile areas: `app/(site)/page.tsx` (25 commits), `components/PartyClient.tsx` (19 commits), and `app/actions.ts` / `app/context/UserContext.tsx` (frequent late-stage test fix commits for allergen handling and reload state). |
| **6: Triage a broken build** | Earned Keep | Evaluated Prompt 6's pre-baked Turbopack Google Fonts failure (`bungee_acefce73` / `sora_3b83333f`). Live execution confirmed that `pnpm typecheck` passes cleanly (0 errors), 482/498 tests pass, and `pnpm build` succeeds completely in an internet-connected environment. The prompt's failure is classified as **Setup / Sandbox Environment (Network/TLS Restriction)** with 100% confidence, not code rot or app defect. |
| **7: Tests for naked code** | Earned Keep | Verified `lib/scoring.ts` had no dedicated test file (`tests/lib/scoring.test.ts` was missing). Implemented `tests/lib/scoring.test.ts` covering happy path (`test_weightedSpin_returns_one_dish_per_reel_with_valid_inputs`), empty reel fallback (`test_weightedSpin_handles_empty_reel_by_generating_placeholder`), and lock handling (`test_weightedSpin_honors_valid_lock_and_ignores_invalid_lock`). Executed live via `npx vitest run tests/lib/scoring.test.ts` and confirmed **3/3 tests passed**. |
| **8: Two-way traceability** | Earned Keep | Executed live `pnpm test`: **87 test files, 498 total tests — 482 passed, 15 failed, 1 skipped** (61.85s). Built two-way mapping between 20 canonical use cases ([usecasestop20.md](usecasestop20.md)) and test files. Identified orphan use cases (UC16 Create Party, UC17 Join Party lack dedicated unit test files outside route integration tests) and orphan test files (`tests/components/ThemeToggle.test.tsx`, `tests/components/ui/Ribbon.test.tsx` map to non-functional UI concerns). |
| **9: Then versus now** | Abandoned | Evaluated `lib/rng.ts` (xmur3 + mulberry32 PRNG). Compared against modern alternatives (`crypto.getRandomValues`, `seedrandom`, `pure-rand`). Concluded that while Web Crypto provides cryptographic security, the current custom PRNG has zero dependencies, minimal footprint, and exact 10-second bucket determinism. Migration offers no practical benefit for slot reel bias; recommended keeping existing code. |
| **10: Honest rewrite** | Earned Keep | Analyzed `components/PlacesMapCard.tsx` map initialization effect. Rewrote the async script loading and map creation flow to eliminate nested promises and unsafe `(window as any)` casting while maintaining identical behavior. Identified missing test coverage for geolocation error fallback (`UNCOVERED`). |
| **11: The dependency map** | Earned Keep | Analyzed `package.json` and `.env.example`. Identified critical boot dependencies (`DATABASE_URL` → `prisma/schema.prisma:1858`, `lib/neon.ts:15`; `@stackframe/stack` → `app/handler/[...stack]/page.tsx`). Found 3 declared but completely unused dependencies: `"auth": "^1.2.3"`, `"next-auth": "^4.24.13"`, and `"neon-js": "^1.1.2"` (zero imports in codebase). |
| **12: The public surface** | Earned Keep | Cataloged all 19 method/path combinations across 17 API routes in `app/api/**/route.ts`. Verified that **NONE FOUND** authorization checks exist on any endpoint (no session verification, client-supplied `auth_id`/`userId` trusted blindly). Flagged `POST /api/user/update` (lets any caller rename any user) and `DELETE /api/dishes/[id]` (lets any caller delete dishes) as highest security risks. |
| **13: Naming and pattern drift** | Earned Keep | Identified 3 major architectural drifts across pasted API files: (1) Auth identifier naming (`auth_id` snake_case vs `authId` camelCase vs `userId`); (2) Error response envelope shapes (`{issues}`, `{code}`, `{message}`, `{error}`); (3) Input validation strategy (Zod `safeParse` in `create`/`saved`/`dishes` vs manual `if (!name)` checks in `user/update`). |
| **14: The data model, reconstructed** | Earned Keep | Reconstructed 6 Prisma entities (`User`, `Favorite`, `Dish`, `Spin`, `Party`, `PartyMember`) from `prisma/schema.prisma`. Pinpointed schema anomalies: `Party.hostId` lacks foreign key relation to `User`, `Dish.tags`/`allergens` stored as CSV strings vs `User.allergens` stored as `String[]` scalar array, and `Dish.cuisineType`/`keyIngredients` fields are unused in application routes. |
| **15: Onboarding from the outside** | Earned Keep | Formulated 6-step local setup checklist. Identified major blocker: README documents SQLite default and `.env.example` sets `DATABASE_URL="file:./dev.db"`, but `prisma/schema.prisma:1857` hardcodes `provider = "postgresql"`, causing `pnpm prisma db push` to fail without Docker or schema modification. Also noted missing `STACK_SECRET_SERVER_KEY` in `.env.example`. |

---

## 2. Caught Issues (Static, Code-Confirmed)

### Issue 1: Missing Authorization Guards Across All Public API Routes
- **Location**: `app/api/user/update/route.ts:1779-1800`, `app/api/user/saved/route.ts:1748-1765`, `app/api/party/create/route.ts:1687-1729`, `app/api/dishes/route.ts:1805-1836`
- **Details**: All 19 API endpoints lack authentication/authorization middleware. Routes accepting `auth_id`, `authId`, or `userId` in the POST request body update user profiles or saved meals without verifying if the caller owns that account session.

### Issue 2: In-Memory Only Rate Limiter Unsuited for Multi-Instance Deployments
- **Location**: `lib/rateLimit.ts:395-434`
- **Details**: The token-bucket rate limiter uses an in-memory `Map<string, Bucket>()`. On serverless or multi-instance deployments (e.g. Vercel / AWS Lambda), process memory is not shared, rendering the 20 requests/minute limit per-instance rather than global.

### Issue 3: Data Type Inconsistency for List-Based Attributes
- **Location**: `prisma/schema.prisma:1868-1891`
- **Details**: `User.allergens` and `User.savedMeals` are defined as native scalar arrays (`String[]`), whereas `Dish.tags` and `Dish.allergens` are defined as plain `String` CSV fields. This forces routes (`app/api/dishes/route.ts:1833`) to manually join and split comma-separated values.

### Issue 4: Missing Foreign Key Constraint on `Party.hostId`
- **Location**: `prisma/schema.prisma:1917`
- **Details**: `Party.hostId` is declared as an unconstrained `String?` without an `@relation` linking it to `User.id` or `PartyMember.id`, leading to potential orphaned host identifiers when users or parties are deleted.

---

## 3. Caught Issues (Execution-Confirmed, Live Session)

Running `pnpm typecheck`, `npx vitest run`, and `pnpm build` live surfaced 15 real test failures across 5 test files:

### Issue 5: Known Regression Defect Catalog (`tests/use-cases-qwen/uc-regression-bugs.test.ts`)
Eight tests in `tests/use-cases-qwen/uc-regression-bugs.test.ts` failed deterministically, confirming 8 unhandled product defects:
1. **BUG-01 (`POST /api/party/leave`)**: Returns `200 OK` on empty `memberId` instead of expected `400 BAD_REQUEST`.
2. **BUG-02 (`GET /api/filters`)**: Returns tags in database insertion order instead of sorted alphabetically.
3. **BUG-03 (`POST /api/user/update`)**: Throws uncaught internal exception (`500`) on malformed JSON body instead of returning `400 BAD_REQUEST`.
4. **BUG-04 (`POST /api/dishes`)**: Returns `tags` and `allergens` as raw CSV strings in `201 Created` response instead of parsed arrays.
5. **BUG-05 (`GET /api/allergens`)**: Returns unsorted `ALLERGEN_OPTIONS` order on database fallback instead of sorted order.
6. **BUG-06 (`GET /api/party/state`)**: Returns `200 OK` for an inactive party (`isActive: false`) instead of `404 NOT_FOUND`.
7. **BUG-07 (`DELETE /api/dishes/[id]`)**: Catches all database exceptions and returns `404 Not Found` instead of `500 Internal Server Error`.
8. **BUG-08 (`PATCH /api/dishes/[id]`)**: Catches all database exceptions and returns `404 Not Found` instead of `500 Internal Server Error`.

### Issue 6: Deterministic Test Failures in Core Use-Case Suites
Re-running the remaining 4 failing test files standalone (`npx vitest run <file>`) confirmed 7 additional deterministic failures:
1. **`tests/use-cases/uc05-07-favorites.test.tsx` (TC-06-01 & TC-06-04)**: `screen.getByText("Dinner")` throws `TestingLibraryElementError: Found multiple elements` because both the filter pill button and dish card category label render the literal text "Dinner" simultaneously.
2. **`tests/use-cases/uc08-places.test.ts` (TC-08-01)**: Assertion `expect(venue.url).toContain("maps.google.com")` fails because the real implementation returns `https://www.google.com/maps/place/?q=place_id:...` (`www.google.com/maps` vs `maps.google.com`).
3. **`tests/use-cases/uc10-13-account.test.ts` (TC-13-01)**: `updateUserDetails` in `app/actions.ts` discards the updated database record and returns the pre-update user name.
4. **`tests/use-cases/uc14-19-party.test.ts` (TC-15-04, TC-15-05, TC-18-03)**: Party API routes return HTTP status `200` instead of `404` for invalid party codes due to missing code validation guards in route handlers.

---

## 4. Strengths & Weaknesses of Gemini 3.6 Flash

### Strengths
- **Strict Rule Compliance**: Adhered strictly to the two-tier evaluation rules, answering static prompts strictly from `prompts.md` content while executing live commands for prompts 6–8.
- **Empirical Execution Precision**: Correctly resolved `pnpm` hoisted installation on exFAT filesystem (`--node-linker=hoisted`), authored 3 passing unit tests for `lib/scoring.ts`, and verified test suite execution down to exact metrics (87 files, 498 tests, 482 passed, 15 failed, 1 skipped).
- **Deep Root-Cause Diagnosis**: Traced test failures directly to underlying code issues (e.g. `updateUserDetails` discarding return values, Zod CSV string serialization gaps, React Testing Library locator ambiguity).

### Weaknesses
- **No Self-Correction on Redundant Package Declarations**: Static inspection correctly identified dead dependencies (`auth`, `next-auth`, `neon-js`), but initial inspection did not automatically generate removal scripts.
- **Strict Formatting Dependency**: Relies on structured prompt inputs to ensure exact line-number citations match between static text snippets and execution logs.

