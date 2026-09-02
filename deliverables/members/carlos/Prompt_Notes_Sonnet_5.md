# Prompt Notes: Model Evaluation on MealSlot (Claude Sonnet 5)

## Executive Summary & Model Configuration

The 15 prompts in [prompts.md](prompts.md) were run against the MealSlot codebase
(`proj2/mealslot`) using **Claude Sonnet 5**. Prompts 1–5, 9-15 were answered
via static exploration of the repo (file tree, README, `git log --stat`, and
targeted source reads). Prompts 6, 7, and 8 require actually running the
build/test pipeline, so in this session `pnpm install` was completed and
`pnpm test`, `pnpm typecheck`, and `pnpm build` were executed for real — see
below for how the environment was unblocked and what running it actually
turned up.

---

## 1. Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| **1: First contact with repo** | Earned Keep | Correctly mapped Next.js 16 App Router (`app/`, no `src/` root), Prisma+Neon, Socket.IO (`ws-server`), Vitest, and a `stack`/`.mcp.json` presence not mentioned in the README. |
| **2: Module to user goals** | Earned Keep | `lib/rateLimit.ts`, `lib/dishes.ts`, `lib/party.ts` map cleanly to goals (throttle spins, generate dish/recipe candidates, coordinate party state) purely from reading the code, no README needed. |
| **3: Use case + edges** | Earned Keep (partial) | Could derive use cases and cite handled extensions (e.g., missing Maps key handled gracefully at [PlacesMapCard.tsx:29-34](proj2/mealslot/components/PlacesMapCard.tsx#L29-L34)); unhandled edges are visible in code but not confirmed by running tests. |
| **4: Undocumented product features** | Earned Keep | README never mentions the in-memory token-bucket rate limiter ([rateLimit.ts](proj2/mealslot/lib/rateLimit.ts)) or the `stack`/handler auth route (`app/handler/[...stack]`). Both are real, code-confirmed hidden features. |
| **5: Rotten / fragile areas** | Earned Keep | `git log --stat` gives real churn counts, not guesses: [app/(site)/page.tsx](proj2/mealslot/app/(site)/page.tsx) (25 touches), [components/PartyClient.tsx](proj2/mealslot/components/PartyClient.tsx) (19), [components/SlotMachine.tsx](proj2/mealslot/components/SlotMachine.tsx) (10) are the top three. |
| **6: Triage a broken build** | Earned Keep | Two real broken builds surfaced and triaged this session: (1) `pnpm install` failing with `ERR_PNPM_EISDIR` on the exFAT `E:` drive — my setup, fixed with `--node-linker=hoisted`; (2) `pnpm build` failing with `Failed to fetch 'Bungee'/'Sora' from Google Fonts` — `next/font/google` requires a live network fetch at build time, which this sandbox doesn't have. Also my setup, not code rot: `pnpm typecheck` passed clean and 476/492 tests pass, so the app itself isn't rotten. |
| **7: Tests for naked code** | Earned Keep | [lib/scoring.ts](proj2/mealslot/lib/scoring.ts) has no dedicated test file (`tests/lib/scoring.test.ts` doesn't exist) — confirmed by diffing `lib/*.ts` against `tests/lib/*.ts`. Its `weightedSpin` export is only exercised indirectly through `spin.route.test.ts` and a couple of `tests/unit/spin*.test.ts` files; the internal `scoreDish` power-up multipliers and `weightedChoice`'s roundoff fallback (line 57–58) are never asserted directly. |
| **8: Two-way traceability** | Earned Keep | Ran the full suite: **85 test files, 492 tests — 476 passed, 15 failed, 1 skipped** (56s). Built a real traceability pass using the `ucNN-...` file-naming convention across `tests/use-cases/` and `tests/use-cases-qwen/` (two independently-authored suites covering the same 20 use cases). Found a genuine orphan-mapping problem: **the `UC-XX:` labels inside `tests/use-cases/*.test.ts` don't match the canonical numbering in [usecasestop20.md](usecasestop20.md)** — e.g. the test suite's "UC-06" is canonical use case #12 (Browse Saved Meals), "UC-08" is canonical #15 (Find Nearby Restaurants), "UC-13" is canonical #6 (Update Display Name). Filename-based traceability is unreliable here; a real matrix needs content-based reconciliation, exactly the trap Prompt 8 warns about. |
| **9: Then versus now** | Abandoned | Same verdict as the Gemini pass — the codebase already uses current Next.js/React idioms, so there's no interesting "then vs. now" delta to explore. |
| **10: Honest rewrite** | Earned Keep | Concrete candidate found without needing to invoke the LLM further: the `setCenter` call in [PlacesMapCard.tsx:101](proj2/mealslot/components/PlacesMapCard.tsx#L101) is a real rewrite target (see below). |
| **11: The dependency map** | Earned Keep | `next-auth`, `auth`, and `neon-js` are all declared in `package.json` but never imported anywhere under `app/`, `lib/`, `components/`, `stack/`, `ws-server/`, or `scripts/` (confirmed by grep, zero hits) — three dead dependencies, not one. Required env vars traced to exact read sites: `DATABASE_URL` → [lib/neon.ts:15](proj2/mealslot/lib/neon.ts#L15), `YOUTUBE_API_KEY` → [lib/youtube.ts:68](proj2/mealslot/lib/youtube.ts#L68), `OPENAI_API_KEY` → [lib/llm.ts:182](proj2/mealslot/lib/llm.ts#L182). |
| **12: The public surface** | Earned Keep | Read all 16 route files under `app/api/**/route.ts`. **None of them contain a session or auth check** — no `getServerSession`, no `stackServerApp.getUser()`, nothing. Every route that needs to know "who is calling" (party join/create, user update, saved meals) just trusts a client-supplied `auth_id`/`authId`/`userId` string in the request body. Riskiest entry, called out below: [app/api/user/update/route.ts](proj2/mealslot/app/api/user/update/route.ts) lets any caller rename any user by supplying their `userId`. |
| **13: Naming and pattern drift** | Earned Keep | Two concrete drifts, both cited file/line below: the same "external auth id" concept is spelled three different ways across routes (`auth_id`, `authId`, `userId`), and error responses use three incompatible envelope shapes (`{error}`, `{code}`, `{message}`) — sometimes two at once in the same object. |
| **14: The data model, reconstructed** | Earned Keep | Reconstructed all 6 models from `prisma/schema.prisma` (see below). Found a real schema inconsistency (`Dish.tags`/`allergens` as `String` vs. `User.allergens`/`savedMeals` as `String[]` for the same "list of tags" concept) and three dead columns (`Party.hostId`, `Dish.cuisineType`, `Dish.keyIngredients`) confirmed unused by grep across `app/`, `lib/`, `components/`. |
| **15: Onboarding from the outside** | Earned Keep | Found a checklist step that would actually block a new engineer: the README documents SQLite as the zero-config default and `.env.example` ships `DATABASE_URL="file:./dev.db"`, but [prisma/schema.prisma:6](proj2/mealslot/prisma/schema.prisma#L6) hardcodes `provider = "postgresql"` — `pnpm prisma db push` with the documented default env will fail. Also flagged: `STACK_SECRET_SERVER_KEY`, which `StackServerApp` needs server-side, is absent from `.env.example` entirely. |

---

## 2. Caught Issues (Static, Code-Confirmed)

### Issue 1: Geolocation race in `PlacesMapCard.tsx` is still present
[PlacesMapCard.tsx:91-107](proj2/mealslot/components/PlacesMapCard.tsx#L91-L107) calls
`navigator.geolocation.getCurrentPosition(...)` and, on success, calls `map.setCenter(here)`.
The `map` reference is captured correctly via closure after `new gm.Map(...)`, so this is
safe in a real browser — but any test or mock that stubs `google.maps.Map` without a
`setCenter` method (as the Gemini run's Vitest output showed for
`PartyMap.test.tsx`) will throw `TypeError: map.setCenter is not a function`. This is a
**test-double gap, not a production runtime bug** — worth noting since the two reports
could otherwise be read as contradictory.

### Issue 2: Rate limiter is in-memory only, undocumented as a scaling limit
[rateLimit.ts:1-11](proj2/mealslot/lib/rateLimit.ts#L1-L11) explicitly comments that the
token bucket is per-process memory, "not shared across instances." On serverless/multi-
instance deployment (e.g., Vercel), this means the 20-spins/minute cap is really
20-per-instance, not a global limit — a real gap between intended and actual behavior
that isn't called out anywhere in the README.

---

## 3. Caught Issues (Execution-Confirmed, this session)

Running `pnpm test`, `pnpm typecheck`, and `pnpm build` for real (see Executive Summary
for how the environment was unblocked) surfaced issues no static read would have caught.

### Issue 3: `tests/use-cases-qwen/uc-regression-bugs.test.ts` is a catalog of 8 known, currently-failing defects
This file is not testing happy paths — every test in it documents a specific, real
behavior gap and is written to fail until the code is fixed:

| ID | Route | Expected | Actual |
|---|---|---|---|
| BUG-01 | `POST /api/party/leave` | 400 on empty `memberId` | 200 |
| BUG-02 | `GET /api/filters` | tags sorted alphabetically | insertion order |
| BUG-03 | `POST /api/user/update` | 400 on malformed JSON body | 500 |
| BUG-04 | `POST /api/dishes` | `tags`/`allergens` as arrays in 201 response | raw CSV strings |
| BUG-05 | `GET /api/allergens` | sorted list on DB-error fallback | unsorted `ALLERGEN_OPTIONS` order |
| BUG-06 | `GET /api/party/state` | 404 for an inactive party | 200 (ignores `isActive`) |
| BUG-07 | `DELETE /api/dishes/[id]` | 500 on a generic DB error | 404 (all exceptions caught as "not found") |
| BUG-08 | `PATCH /api/dishes/[id]` | 500 on a generic DB error | 404 (same catch-all) |

Confirmed via `pnpm test` output (85 files, 492 tests, 15 failed) — these are exactly
8 of the 15 failures.

### Issue 4: 7 more test failures, confirmed real (not test-order flakiness)
The remaining 7 failures span 4 files under `tests/use-cases/`. Because two independent
test suites (`use-cases/` and `use-cases-qwen/`) run in the same process, the first
instinct was to suspect shared-mock pollution across files. That was checked directly:
re-running each of the 4 files completely alone (`npx vitest run <file>`) reproduced the
exact same failures every time — these are deterministic, not order-dependent.

- **`uc05-07-favorites.test.tsx` (TC-06-01, TC-06-04): test bug, not a product bug.**
  `screen.getByText("Dinner")` matches two elements at once — the category filter pill
  and a dish card's category label both render the literal text "Dinner" simultaneously.
  RTL's single-match `getByText` throws `Found multiple elements`. The UI is doing what
  it should; the test's locator is too loose.
- **`uc08-places.test.ts` (TC-08-01): stale assertion.** Test expects the returned map
  URL to contain `"maps.google.com"`; the real implementation returns
  `https://www.google.com/maps/place/?q=place_id:...` — a valid, more specific
  place-id deep link. The test's string check predates this URL format.
- **`uc10-13-account.test.ts` (TC-13-01): code-confirmed, traced to root cause.**
  [app/actions.ts:75-97](proj2/mealslot/app/actions.ts#L75-L97) — `updateUserDetails`
  calls `prisma.user.update(...)` but **discards its return value** and instead returns
  `getUserDetails(userId)`, a separate re-fetch. The test only mocks `prisma.user.update`
  to resolve with the new name, so the second, unmocked read returns stale data. In
  production this isn't a correctness bug (the re-fetch hits the real, now-updated row),
  but it is a real inefficiency — an extra round-trip on every update — and the test's
  contract assumption (`update()`'s return value is what's returned) doesn't match the
  implementation.
- **`uc14-19-party.test.ts` (TC-15-04, TC-15-05, TC-18-03): real status-code mismatches**
  on party-code validation (join with a nonexistent code, join when the auth user isn't
  in the DB yet, and stale invite-code lookup) — same class of gap as BUG-06 above
  (routes not consistently validating existence/state before responding 200).

### Issue 5: 4 unhandled `ERR_REQUIRE_ESM` errors from `jsdom`/`parse5` — real dependency-version drift
Every DOM-based test run logs `require() of ES Module .../parse5/dist/index.js ...
not supported`, from `jsdom/lib/jsdom/browser/parser/html.js`. This doesn't fail any
test (all 476 passing tests still pass), but it's a genuine `code rot` signal per
Prompt 5/6's framing: the installed `parse5` version ships ESM-only while `jsdom`
still `require()`s it as CommonJS. Cheap fix: pin `parse5` to the last CJS-compatible
version, or wait for the `jsdom` release that switches to dynamic `import()`.

---

## 4. Caught Issues (Static, Prompts 11–15)

### Issue 6: No API route checks who is actually calling it
None of the 16 handlers under `app/api/**/route.ts` verify a session before acting on a
caller-supplied identity. [app/api/user/update/route.ts:15-49](proj2/mealslot/app/api/user/update/route.ts#L15-L49)
reads `userId` straight from the request body and passes it to `updateUserDetails` with
no check that the request actually came from that user — the same is true of
`auth_id`/`authId` in `party/create`, `party/join`, and `user/saved`. Stack Auth
(`stack/server.ts`) is installed and configured for exactly this purpose but none of
these routes call it. This is the single riskiest finding in the whole exercise: as
written, any client can rename or modify another user's saved meals by guessing or
enumerating their `auth_id`.

### Issue 7: The same identifier has three different names across the API
The "external auth id" concept is spelled three ways depending on which route you're
in: `auth_id` (snake_case) in
[party/create/route.ts:16](proj2/mealslot/app/api/party/create/route.ts#L16) and
`party/join`, `authId` (camelCase) in
[user/saved/route.ts:14](proj2/mealslot/app/api/user/saved/route.ts#L14), and `userId`
(different word entirely) in
[user/update/route.ts:18](proj2/mealslot/app/api/user/update/route.ts#L18). Same for
error responses: `{error: "..."}` in `dishes/[id]`, `user/create`, `user/update`;
`{code: "NOT_FOUND"|"INTERNAL"|...}` in `party/*`, `spin`, `places`; `{message: "..."}`
in `user/saved` and part of `spin`'s validation path;
[dishes/route.ts:105](proj2/mealslot/app/api/dishes/route.ts#L105) uses `{code,
message}` together. The `{code: ...}` shape looks like the newer, more deliberate
pattern — it's what the `uc-regression-bugs.test.ts` suite (see Section 3) asserts
against — while the bare `{error: "string"}` shape looks like the original,
un-migrated convention.

### Issue 8: `Dish.tags`/`allergens` are modeled differently from `User.allergens`/`savedMeals`
In [prisma/schema.prisma](proj2/mealslot/prisma/schema.prisma), `User.savedMeals` and
`User.allergens` are `String[]` (real Postgres arrays), but `Dish.tags` and
`Dish.allergens` (lines 39-40) are plain `String` — meant to hold comma-separated
values. Same underlying concept ("a list of tags"), two different representations in
the same schema. This isn't hypothetical: it's the exact root cause the
execution-confirmed BUG-04 regression test (Section 3, Issue 3) catches — the dishes
API returns these fields as raw CSV strings instead of arrays because that's genuinely
what's stored.

### Issue 9: Three dead columns in the schema
`Party.hostId`, `Dish.cuisineType`, and `Dish.keyIngredients` are declared in
`prisma/schema.prisma` but never read anywhere under `app/`, `lib/`, or `components/`
(confirmed by grep). Notably, party "host" status is actually computed at runtime from
realtime presence in
[PartyClient.tsx:205](proj2/mealslot/components/PartyClient.tsx#L205)
(`livePeers.find(p => p.creator)?.id`), completely bypassing the persisted `hostId`
column — the schema field and the actual application logic have quietly diverged.

### Issue 10: Onboarding is blocked by a documentation/schema mismatch, and two silent env-var name mismatches
The README's "Quick Start" and `.env.example`'s `DATABASE_URL="file:./dev.db"` both
imply SQLite works out of the box, but
[prisma/schema.prisma:6](proj2/mealslot/prisma/schema.prisma#L6) hardcodes
`provider = "postgresql"` — a fresh clone following the documented steps literally hits
a Prisma error on `db push`. Separately, two env var names don't match between
`.env.example` and the code that reads them: `.env.example` defines
`NEXT_PUBLIC_GOOGLE_MAPS_KEY`, but
[PartyMap.tsx:95](proj2/mealslot/components/PartyMap.tsx#L95) reads
`NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` instead (a different variable, silently `undefined`);
and `.env.example` defines `WS_URL`, but
[lib/realtime.ts:109](proj2/mealslot/lib/realtime.ts#L109) reads
`NEXT_PUBLIC_WS_URL`. Both fail silently rather than erroring — the affected feature
(party map pins, or cross-device realtime) just quietly doesn't work.

---

## 5. Strengths & Weaknesses of Claude Sonnet 5 on This Task

### Strengths
1. **Evidence-first churn ranking** — `git log --stat` gave exact touch counts instead of
   guessing which files are "fragile," directly satisfying Prompt 5's "no folklore" rule.
2. **Cross-file confirmation** — verified the Gemini report's `map.setCenter` finding
   against current source rather than trusting it, and reclassified it as a mocking gap.
3. **Didn't stop at "tests fail"** — for the 7 non-seeded failures, went one level deeper
   than the raw Vitest output: reproduced each file in isolation to rule out test-order
   pollution, and for TC-13-01 traced the failure to the actual line in `actions.ts`
   causing it, rather than reporting "assertion mismatch" and moving on.
4. **Fixed the real blocker instead of reporting around it** — the exFAT/pnpm symlink
   failure would have kept prompts 6–8 unanswerable; diagnosing it and switching to
   `--node-linker=hoisted` is itself a correctly-triaged Prompt 6 answer.

### Weaknesses
1. **Traceability matrix is a spot-check, not exhaustive** — the UC-numbering mismatch
   between `tests/use-cases/` and `usecasestop20.md` was caught by sampling test labels
   against the canonical doc, not by building all ~30 rows of a full test-to-use-case
   matrix; a complete matrix would still take a dedicated pass.
2. **Root-caused one failure, asserted the rest** — the `updateUserDetails` refetch bug
   (Issue 4) was traced to source; TC-08-01 and the party-code failures (TC-15-04/05,
   TC-18-03) were classified from assertion diffs alone, without reading the corresponding
   route handlers line-by-line to confirm which side (test or implementation) is "correct."
