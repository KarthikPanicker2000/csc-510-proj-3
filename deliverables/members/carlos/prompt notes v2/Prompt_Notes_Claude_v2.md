# Prompt Notes v2: Model Evaluation on MealSlot (Claude Sonnet 5)

## Executive Summary & Model Configuration

The 15 prompts in [prompts.md](prompts.md) were answered by **Claude Sonnet 5**
(`claude-sonnet-5`) under a stricter, two-track protocol than the earlier
`Prompt_Notes_Sonnet_5.md` run in this repo:

- **Prompts 1–5 and 9–15** were answered from **prompts.md's pasted content
  only** — no reads of `proj2/mealslot`'s live source, no shell exploration
  beyond what's already quoted in the prompt file. Every citation below for
  these prompts is a `prompts.md:LINE` reference, checkable against the
  prompt file itself, specifically so this run is comparable apples-to-apples
  against the same static input given to Gemini and Codex. Prompt 3's
  `usecases0.md` substitution (using [usecasestop20.md](usecasestop20.md)
  instead, per prompts.md's own note at line 441) was accepted as specified.
- **Prompts 6, 7, and 8 required actually running the project.** `pnpm` was
  installed fresh (`npm install -g pnpm@10.24.0`), dependencies were
  installed with `pnpm install --frozen-lockfile --node-linker=hoisted`
  (required — this repo lives on an exFAT drive, and pnpm's default
  symlink-based install strategy fails there with `ERR_PNPM_EISDIR`), and
  `pnpm typecheck`, `pnpm test`, and `pnpm build` were run for real, with
  full output captured and read (not just tails). Prompt 7's new test file
  was written and executed against the real implementation before being
  reported as done. Every failure surfaced by `pnpm test` was re-run in
  isolation to confirm it wasn't test-order flakiness before being reported
  as real — one genuinely was order-dependent (see Issue 5), and the other
  15 were not.

This run's standout finding, not present in any of the three prior reports in
this repo: `pnpm test`'s own summary line quietly under-reports failure.
Four real test files (21 test cases) are **silently never collected at
all** by Vitest — not failed, not skipped, just absent from both the pass
and fail counts — because of a dependency-version mismatch between `jsdom`
and `parse5`. See Issue 5.

---

## 1. Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| **1: First contact with repo** | Earned Keep | From tree + README alone: ranked `prisma/schema.prisma`, `package.json`, `app/layout.tsx`, `lib/schemas.ts`, and the README itself as the five files that matter most — each justified by a specific README line (e.g. `lib/schemas.ts` because the README itself calls it the single source of truth for API validation, prompts.md:290). Flagged `assets/` (one video file, no code) as safe to ignore this month. Did not need to ask for anything further — the tree + README were sufficient for a top-level orientation. |
| **2: Module to user goals** | Earned Keep | `lib/rateLimit.ts` serves exactly one user goal (throttle spin-style API abuse per IP) with a clean 5-step flow, all derivable from the code alone with no README needed. Cited the concrete handled failure (429 + `RATE_LIMIT` + `retryAfterMs`, prompts.md:422-428). Correctly reported **no dead code** — every declaration in the module is reachable from the one exported function — rather than force-inventing an item to fill the "dead code" ask. |
| **3: Use case + edges** | Earned Keep | Wrote UC7 (View Recipe Videos) in the exact table format from the worked example. Three handled extensions cited with lines (missing key → stub fallback with notice, prompts.md:566-593; per-dish HTTP error isolated to that dish, prompts.md:500,539-543; malformed body → 400, prompts.md:521-526). Three unhandled extensions identified and defended from the code: a dish with zero YouTube results is indistinguishable from an error (empty array, no error set); a YouTube response-shape change would throw inside `mapped` (line ~545) with only a generic caught-error message surfacing to the user; a 403 quota-exceeded response is treated identically to any other failure with no distinguishing message. |
| **4: Undocumented product features** | Earned Keep | Ranked hidden features strictly from the given route/function lists against the README's own claims. Top finding: the README's Roadmap still lists "Add a login system" as *future* work (prompts.md:345) while the function list shows a working account system already exists (`ensureUserInDB`, `getUserDetails`, `updateUserDetails`, `/api/user/create`, `/api/user/update`, `/api/user/saved`, prompts.md:629-631,655-657) — the single largest doc/reality gap. Also caught and *rejected* a false-positive candidate: `lib/rateLimit.ts` looked hidden at first glance but the README's own "Validation & Rate Limiting" section already documents it (prompts.md:288-292) — did not over-claim. |
| **5: Rotten / fragile areas** | Earned Keep | Ranked `app/(site)/page.tsx` (25 touches, prompts.md:821, last touched 2025-12-07), `components/PartyClient.tsx` (19 touches, prompts.md:825, co-occurring with page.tsx in the same rapid-fire same-day commits at prompts.md:715-719,733-736), and the `SlotMachine.tsx`/`spin/route.ts` pair (10 and 9 touches, prompts.md:828,830, same last-touch date) using only churn counts + recency + commit-message patterns given. Explicitly flagged that TODO/FIXME density and 50+-line function counts — two signals the prompt invites — were **not derivable** from the pasted `git log --stat` excerpt, rather than fabricating them. |
| **6: Triage a broken build** | Earned Keep | Ran a real `pnpm build` in this sandbox and reproduced the exact font-fetch TLS failure independently (not copied from the prompt's pre-baked text) — then went four layers deeper than the given error message. See Section 2, Issue 1 for the full root-cause chain: TLS-intercepted sandbox network (your setup, high confidence, fix verified) → missing `.env.local` (your setup) → `STACK_SECRET_SERVER_KEY` absent from `.env.example` entirely (real repo gap) → `.env.example`'s own placeholder value for `NEXT_PUBLIC_STACK_PROJECT_ID` fails Stack Auth's own UUID validation (real bug — the README's "stubs work without keys" claim does not hold for the build step). `pnpm typecheck` passed with zero output, confirming the underlying app is not rotten — only the production build path was blocked, and not solely by this sandbox's network. **Re-confirmed end-to-end**: once a `.env.local` with real Stack Auth / Maps / YouTube credentials was placed in the repo, `pnpm build` (still with the TLS env var) completed cleanly — exit 0, 17/17 static pages generated, all 23 routes compiled — closing the loop on every layer of the diagnosis. |
| **7: Tests for naked code** | Earned Keep | Wrote `tests/lib/scoring.test.ts` (3 tests: happy path, locked-dish honored, empty-reel placeholder) with sentence-style names and a "This proves ..." line each, per the prompt's rules. Explicitly stated the assumption that `scoreDish`/`weightedChoice` can't be tested in isolation since they aren't exported. **Actually ran it** against the real `lib/scoring.ts` — `npx vitest run tests/lib/scoring.test.ts` → 3/3 passed — before reporting it done, and cited real file:line for each behavior (lib/scoring.ts:88-101, 104-112). |
| **8: Two-way traceability** | Earned Keep | Ran the full suite for real: **85 files collected, 79 passed / 6 failed; 492 tests, 475 passed / 16 failed / 1 skipped.** Built the traceability table by grepping actual `describe()` titles across all 90 files the prompt lists (not guessing from filenames) — found the internal `UC-NN:` labels inside `tests/use-cases/` and `tests/use-cases-qwen/` form **two more numbering schemes**, both independent of the canonical `usecasestop20.md` numbers and independent of each other (e.g. `uc02-lock-respin.test.ts` is labeled `UC-02` internally but its content is canonical UC5; the same canonical use case appears as `UC-17` in one suite's spin-machine test and matches by content, not number, elsewhere). Confirmed two real UC gaps (UC18 Sign In, UC19 Sign Out — no test anywhere actually exercises a sign-in/out action) and one true orphan test with no UC mapping at all (`uc20-theme.test.tsx`, Theme toggling isn't among the 20 canonical use cases). Also discovered, independent of anything the prompt asked for, that 4 real test files never even get collected (Issue 5) — a bigger and more important finding than the numbering-scheme confusion. |
| **9: Then versus now** | Earned Keep | Proposed `pure-rand` (the seeded-PRNG library used by `fast-check`) as the concrete current-mainstream substitute for the hand-rolled `xmur3`+`mulberry32` combo. Verdict, no diplomacy: the old code wins — it's ~50 dependency-free lines that are fully readable in under a minute, versus a supply-chain addition that buys statistical rigor nobody asked for. Migration would also silently change every existing seed's output sequence, breaking any test or demo that assumes a specific spin result for a specific seed. Recommendation: don't migrate. Unlike the predecessor Sonnet 5 report (which marked this prompt "Abandoned" for lacking an interesting delta), this run produced a real, defensible, non-diplomatic verdict rather than declining to answer. |
| **10: Honest rewrite** | Earned Keep | Rewrote the `PlacesMapCard` map-init effect: extracted `loadGoogleMaps` to a pure module-level function (it never depended on props/state, so recreating it every render was pure waste) and split the async IIFE into a named `renderMap(container, isCancelled)` step, while deliberately preserving the pre-existing latent bug where a second effect run reusing an *already-loaded* `#gmaps-sdk` script tag waits on a `'load'` event that will never re-fire (out of scope per the "identical behavior" constraint — flagged, not fixed). For every change: honestly marked **UNCOVERED** — the prompt supplies four test *filenames* (prompts.md:1485-1488) but never their contents, so no specific test can be named with confidence as the one that would catch a regression. That gap is itself a finding about the prompt's own design, not just the codebase. |
| **11: The dependency map** | Earned Keep | Cross-referenced `.env.example`'s own inline comments (prompts.md:1612,1617) to correctly separate vars explicitly marked optional/stubbed (`MAPS_API_KEY`, `YOUTUBE_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_CLIENT_ID/SECRET`, `AUTH_SECRET`) from the three with no such disclaimer (`DATABASE_URL`, `NEXT_PUBLIC_STACK_PROJECT_ID`, `NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY`) — the latter are the real startup-blocking candidates. Explicitly declined to cite fabricated `lib/*.ts:LINE` read-sites for them, since no source code is pasted anywhere in prompts.md that shows where they're read — correctly named this as a "tell me what to paste next" gap (`lib/db.ts`, `stack/client.ts`, `stack/server.ts`) instead of guessing. For the unused-dependency ask: named the bare `auth` package (prompts.md:1540) — it never appears in Prompt 4's exhaustive function/route list, the README, or the directory tree, while the real auth surface (`stack/`, `app/handler/[...stack]`) is visibly present and used everywhere else in the pasted material. |
| **12: The public surface** | Earned Keep | Prompt 12 itself pastes only method+path, no handler bodies — so by the letter of its own "don't guess, write NONE FOUND" rule, most of the 18 routes are honestly unverifiable *from this prompt alone*. But 6 of the 18 have real source pasted elsewhere in prompts.md (Prompt 2's `rateLimit.ts`, Prompt 3's `videos/route.ts`, Prompt 7's `spin/route.ts`, Prompt 13's `party/create`, `user/saved`, `user/update`, `dishes` POST) — cross-referencing those, confirmed **zero** of the 6 verifiable routes have any session/auth check; all trust a client-supplied id. Flagged `POST /api/user/update` (prompts.md:1773-1800) as the single riskiest confirmed entry: any caller can rename any user by supplying their raw `userId`, with no ownership check at all. The other 12 routes are marked "NONE FOUND — no handler source provided to verify" rather than assumed safe or assumed vulnerable. |
| **13: Naming and pattern drift** | Earned Keep | Two independent drifts, both fully cited within the 4 pasted files. (1) The "who is calling" field is spelled `auth_id` (prompts.md:1684,1704), `authId` (prompts.md:1744,1755), and `userId` (prompts.md:1782) across the four routes. (2) `user/update/route.ts` is the consistent holdout across three separate axes at once: it's the only one of the four skipping Zod validation for hand-rolled `if` checks (prompts.md:1784,1788), the only one returning `NextResponse.json` instead of the other three's bare `Response.json` (prompts.md:1776 vs. 1692/1752/1809), and the only one using a bare `{error: "..."}` envelope (prompts.md:1785,1789,1797) instead of the `{code}`/`{code, message}` shapes the other three converge on (prompts.md:1728,1821). |
| **14: The data model, reconstructed** | Earned Keep | Reconstructed all 6 models into a table from the schema alone. Led with the strongest schema-only-provable finding: `User.savedMeals`/`User.allergens` are modeled as raw `String[]` (prompts.md:1868-1869) with zero referential integrity to `Dish.id`, while the *same* "user favorited a dish" concept is *also* modeled properly via the `Favorite` join table with real FKs (prompts.md:1878-1884) — the same relationship exists twice, once enforced and once not. Second finding: `Party.hostId` (prompts.md:1917) is a bare `String?`, not a `@relation`, unlike every structurally similar field in the file — a relationship-shaped field that isn't declared as one. Correctly caveated that "fields unused elsewhere in the code" can only be a *candidate list* from schema + Prompt 4's function-signature list alone (no function bodies were pasted for Prompt 14), not a proven-dead-code claim. |
| **15: Onboarding from the outside** | Earned Keep | Built a step-by-step checklist from the README's Quick Start, marking each step GIVEN or STUCK. Two concrete stuck points: (1) `pnpm prisma db push`, at the exact step the README (prompts.md:277-279) claims "SQLite (zero-config)" while the schema pasted elsewhere in prompts.md (Prompt 14, prompts.md:1857) hardcodes `provider = "postgresql"` — a real, immediate blocker with no default that works. (2) `.env.example` (prompts.md:1599-1625) never lists `STACK_SECRET_SERVER_KEY` despite `@stackframe/stack` being a real, used dependency — a new engineer following the file verbatim has no way to know it's needed. Also caught a direct self-contradiction inside the repo's own docs: the README says to "populate the keys... for full functionality" (prompts.md:210-213) while `.env.example`'s own comment on the same two variables says they're "optional; stubs are used if empty" (prompts.md:1617). |

---

## 2. Caught Issues (Execution-Confirmed, Prompts 6–8)

### Issue 1: `pnpm build` fails through three independent, stacked layers — triaged per Prompt 6's own rubric

Running `pnpm build` fresh in this sandbox reproduced the exact font-fetch TLS
error from the prompt's pre-baked text, independently:

```
Error while requesting resource
There was an issue establishing a connection while requesting https://fonts.googleapis.com/css2?family=Bungee...
Hint: ... Try enabling system TLS certificates with NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1 ...
```

Triage, going past the surface error rather than stopping at it:

1. **Font fetch — YOUR SETUP, high confidence, fix verified.** `curl` to
   `fonts.googleapis.com` and to `registry.npmjs.org` both failed cert
   verification identically ("unable to get local issuer certificate"), but
   both succeeded instantly with `-k` (skip verification) — this sandbox
   sits behind a TLS-intercepting proxy whose CA isn't in the default trust
   store Turbopack's Rust-based font fetcher uses (Node's own HTTPS client,
   used by `pnpm install`, evidently trusts it via a different path).
   Setting `NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1` — exactly the
   hint in the error text — got the build past this step, confirming the
   diagnosis rather than just asserting it.
2. **No `.env.local` — YOUR SETUP.** With the TLS var set, the next failure
   was `Error: Welcome to Stack Auth! ... you haven't provided a project ID`
   for every page. No `.env.local` existed (only `.env.example`). Copying it
   per the README's own documented step (`cp -n .env.example .env.local`)
   moved the failure forward.
3. **`STACK_SECRET_SERVER_KEY` missing from `.env.example` — REAL REPO GAP,
   high confidence.** The next failure was `No secret server key provided.
   Please copy your key... and put it in the STACK_SECRET_SERVER_KEY
   environment variable.` — grepping `.env.example`'s full pasted contents
   confirms this variable is never declared there at all, despite
   `@stackframe/stack` being a real, used dependency. Adding a stub value
   moved the failure forward again.
4. **`.env.example`'s own placeholder value is invalid — REAL BUG, high
   confidence.** The final failure: `Invalid project ID:
   your_stack_project_id. Project IDs must be UUIDs.` — `.env.example`'s
   literal placeholder text for `NEXT_PUBLIC_STACK_PROJECT_ID` fails Stack
   Auth's own constructor-time validation. This directly contradicts the
   README's "Basic flows work with no secrets (deterministic stubs
   auto-activate)" claim (prompts.md:273) — there is no stub path for Stack
   Auth at build time; it hard-fails without a real, valid project.

**What this says about overall app health:** `pnpm typecheck` passed with
zero output (see below) and 475/492 tests pass — the application code
itself is not rotten. The build is blocked end-to-end for *anyone* without
real Stack Auth credentials, in any environment, not just this sandbox —
that's a real onboarding/CI gap, not merely "my machine."

```
> mealslot@0.1.0 typecheck
> tsc -p tsconfig.json --noEmit
(zero errors, zero warnings, exit 0)
```

**Confirmation pass:** once a `.env.local` populated with real Stack Auth
project/publishable/secret keys and real Maps/YouTube keys was placed in the
repo, `NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1 pnpm build` exited
0 cleanly:

```
 ✓ Compiled successfully in 7.1s
 ✓ Generating static pages using 15 workers (17/17) in 4.3s

Route (app)
┌ ƒ /
├ ƒ /_not-found
├ ƒ /account
├ ƒ /api/allergens          ├ ƒ /api/party/spin        ├ ƒ /api/user/create
├ ƒ /api/dishes             ├ ƒ /api/party/state       ├ ƒ /api/user/saved
├ ƒ /api/dishes/[id]        ├ ƒ /api/party/update      ├ ƒ /api/user/update
├ ƒ /api/filters            ├ ƒ /api/places            ├ ƒ /api/videos
├ ƒ /api/party/create       ├ ƒ /api/recipe            ├ ƒ /auth/callback
├ ƒ /api/party/join         ├ ƒ /api/spin              ├ ƒ /favorites
├ ƒ /api/party/leave        └ ...                      ├ ƒ /handler/[...stack]
                                                         └ ƒ /party

ƒ  (Dynamic)  server-rendered on demand
```

Notably, the `.env.local` used for this pass still points `DATABASE_URL` at
a local Postgres (`localhost:5432`) that isn't actually running in this
sandbox — and the build didn't care, because every route above is `ƒ
(Dynamic)`, none are statically prerendered with a build-time DB read. This
sharpens the earlier diagnosis: the build's only hard dependency is on
**valid** Stack Auth values (a real UUID project ID + a server key that
passes construction-time validation), not on a live database. That's a
narrower, more precise "what do I actually need before `pnpm build` will
succeed" answer than the README gives anywhere.

### Issue 2: `lib/scoring.ts`'s `weightedSpin` now has a real, passing test file

Added `tests/lib/scoring.test.ts` (3 tests, all passing against the real
implementation, `npx vitest run tests/lib/scoring.test.ts` → 3/3):

```typescript
import { describe, it, expect } from "vitest";
import { weightedSpin } from "../../lib/scoring";
import type { Dish } from "../../lib/schemas";

// Assumption: scoreDish() and weightedChoice() are not exported from
// lib/scoring.ts, so they cannot be imported and tested in isolation from
// outside the module. These tests exercise them only indirectly, through
// the public weightedSpin() entry point.

function makeDish(overrides: Partial<Dish> & { id: string }): Dish {
  return {
    name: overrides.id,
    category: "Dinner",
    tags: [],
    costBand: 2,
    timeBand: 2,
    isHealthy: false,
    allergens: [],
    ytQuery: "quick recipe",
    ...overrides,
  };
}

describe("weightedSpin", () => {
  it("test_returns_one_dish_per_reel_drawn_from_that_reel_when_no_locks_or_powerups_are_given", () => {
    const reelA: Dish[] = [makeDish({ id: "a1" }), makeDish({ id: "a2" })];
    const reelB: Dish[] = [
      makeDish({ id: "b1" }),
      makeDish({ id: "b2" }),
      makeDish({ id: "b3" }),
    ];
    const result = weightedSpin([reelA, reelB]);
    expect(result).toHaveLength(2);
    expect(reelA.map((d) => d.id)).toContain(result[0]!.id);
    expect(reelB.map((d) => d.id)).toContain(result[1]!.id);
  });
  // This proves weightedSpin always returns exactly one dish per input reel,
  // and that dish is a genuine member of that reel, for the default
  // no-locks/no-powerups path.

  it("test_honors_a_locked_dish_that_exists_in_its_reel", () => {
    const target = makeDish({ id: "locked-target" });
    const reel: Dish[] = [makeDish({ id: "other" }), target, makeDish({ id: "another" })];
    const result = weightedSpin([reel], [{ index: 0, dishId: "locked-target" }]);
    expect(result).toEqual([target]);
  });
  // This proves a lock takes precedence over the weighted-random pick
  // whenever the locked dishId is present in that reel (lib/scoring.ts:104-112),
  // deterministically, regardless of the RNG's seed/time bucket.

  it("test_fills_an_empty_reel_with_a_placeholder_dish_instead_of_throwing", () => {
    const result = weightedSpin([[]]);
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      id: "placeholder_0",
      name: "No options",
      category: "unknown",
    });
  });
  // This proves an empty reel never causes weightedSpin to throw or return
  // undefined; it manufactures the hardcoded placeholder dish defined at
  // lib/scoring.ts:88-101 instead.
});
```

This file has been left in the repo at
[proj2/mealslot/tests/lib/scoring.test.ts](proj2/mealslot/tests/lib/scoring.test.ts)
as a real, working artifact of this run.

### Issue 3: Real, execution-confirmed traceability numbers for Prompt 8

Full suite: **85 test files collected — 79 passed / 6 failed. 492 tests —
475 passed / 16 failed / 1 skipped.**

**The `UC-NN:` labels inside the two use-case suites are three independent
numbering schemes, none matching the canonical `usecasestop20.md` numbers or
each other** (confirmed by grepping every `describe()` title, not by
filename):

| Test file | Internal label(s) (grepped) | Canonical UC (by content) |
|---|---|---|
| `tests/use-cases/uc01-03-04-spin.test.ts` | UC-01 Spin Solo Meal Selection | UC1 Spin for a Meal |
| | UC-03 Apply Dietary Filters to a Spin | (extension of UC1, not canonical UC3 "Vote") |
| | UC-04 Activate Power-Ups for a Spin | UC11 Apply Power-Ups to Bias Selection |
| `tests/use-cases/uc02-lock-respin.test.ts` | UC-02 Lock a Reel and Re-spin | UC5 Lock a Reel and Re-Spin |
| `tests/use-cases/uc05-07-favorites.test.tsx` | UC-05 Save a Dish to Favorites | UC8 Save a Meal to Favorites |
| | UC-06 Browse and Filter Saved Meals | UC12 Browse Saved Meals |
| | UC-07 Remove a Saved Meal | UC13 Remove a Saved Meal |
| `tests/use-cases/uc08-places.test.ts` | UC-08 Find Nearby Restaurants After Spinning | UC15 Find Nearby Restaurants After Spinning |
| `tests/use-cases/uc09-videos.test.ts` | UC-09 View Recipe Videos for a Dish | UC7 View Recipe Videos for a Dish |
| `tests/use-cases/uc10-13-account.test.ts` | UC-10 Register an Account | UC10 Register an Account (matches!) |
| | UC-13 Update Display Name | UC6 Update Display Name |
| `tests/use-cases/uc14-19-party.test.ts` | UC-14 Create a Party | UC16 Create Party |
| | UC-15 Join a Party (2/3 tests FAIL — see below) | UC17 Join Party |
| | UC-16 Submit Personal Preferences for a Party | UC2 Set Party Dietary Preferences and Resolve Conflicts |
| | UC-17 Spin the Party Slot Machine | UC4 Spin the Party Slot Machine (matches!) |
| | UC-18 Share a Party Invite Code (1/1 test FAILS) | supports UC17 Join Party |
| | UC-19 Leave a Party | UC14 Leave a Party |
| `tests/use-cases/uc20-theme.test.tsx` | UC-20 Toggle Light/Dark Theme | **no canonical UC — real orphan** |
| `tests/use-cases-qwen/uc01-02-03-party-crud.test.ts` | UC-01 Join Party / UC-02 Create Party / UC-03 Leave Party | UC17 / UC16 / UC14 |
| `tests/use-cases-qwen/uc04-05-06-spin-prefs-state.test.ts` | UC-04 Spin Meal / UC-05 Update Preferences / UC-06 View Party State | UC4 / UC2 / (infra, no canonical UC) |
| `tests/use-cases-qwen/uc07-search-restaurants.test.ts` | UC-07 Search Restaurants | UC15 |
| `tests/use-cases-qwen/uc08-09-recipe-video.test.ts` | UC-08 Generate Recipe / UC-09 View Recipe Video | (no canonical UC — recipe generation isn't in the 20) / UC7 |
| `tests/use-cases-qwen/uc10-11-filters-allergens.test.ts` | UC-10 Filter Dishes / UC-11 View Allergens | UC9 (both, supporting) |
| `tests/use-cases-qwen/uc12-13-user.test.ts` | UC-12 Save Meal / UC-13 Update Profile | UC8 / UC6 |
| `tests/use-cases-qwen/uc15-17-18-dishes-party-members.test.ts` | UC-15 View Dish Details / UC-17 View Party Members / UC-18 View Dish Tags | (no canonical UC — dish admin/party-roster infra, not in the 20) |
| `tests/use-cases-qwen/uc-regression-bugs.test.ts` | BUG-01..08 (defect regression tests, not UC-labeled) | mixed, see Issue 4 |

**Two canonical use cases have no real behavioral test anywhere in the
suite**, confirmed by content search (not just filename), which is a real
gap, not a filename artifact:
- **UC18 Sign In to an Account** — the closest tests
  (`tests/app/auth/callback/AuthPage.test.tsx`,
  `tests/app/handler/[...stack]/HandlerPage.test.tsx`) test the callback/handler
  *pages render*, not a sign-in action and its effect.
- **UC19 Sign Out of an Account** — `tests/components/UserMenu.test.tsx`
  accepts an `onSignOut` prop but never clicks a sign-out control or asserts
  the callback fires; confirmed by reading the file in full.

One canonical use case, **UC3 Vote on a Spin Result**, *is* genuinely well
covered but by content rather than by any UC-labeled file — grepping "vote"
across the whole suite (not just describe-title grepping, which would have
missed this) surfaces real coverage in `tests/components/party/PartySpinMachine.test.tsx`
(vote button wiring), `tests/integration/party/party.integration.test.ts`
(vote up/reroll/toggle integration), and `tests/unit/party/party.unit.test.ts`
(`canVoteOnDish` gating) — a useful reminder that UC-traceability-by-filename
alone would have produced a false negative here.

**Tests that map to no use case at all** (confirmed by content, not just
absence of a "uc" prefix): all of `tests/components/ui/*`, `Modal`,
`Toast`, `ClientMount`, `HeaderServer`, `StackWrapper`, `app/layout.test.tsx`,
`app/loading.test.tsx`, `tests/lib/neon.test.ts`, `tests/unit/apiRoutes.test.ts`,
`tests/app/api/routes.test.ts` (generic infra/smoke, not user-facing
behavior); `tests/components/ThemeToggle.test.tsx` +
`tests/use-cases/uc20-theme.test.tsx` (theme toggling isn't one of the 20);
`tests/app/api/dishes/*.route.test.ts`, `tests/app/api/recipe/recipe.route.test.ts`,
`tests/lib/llm.test.ts`, `tests/unit/recipeSchema.test.ts` (dish-admin CRUD
and recipe generation are real features per Prompt 4 but aren't among the 20
canonical use cases either).

### Issue 4: 15 of the 16 reported test failures are real and deterministic; 1 is order-dependent

Every failing file was re-run alone with `npx vitest run <file>` to rule out
shared-mock pollution. 15 of 16 reproduced identically in isolation — real,
not flaky:

| Test | Expected | Actual | Root cause |
|---|---|---|---|
| BUG-01 `party/leave` | 400 on empty `memberId` | 200 | `z.string()` accepts `""`; no non-empty check |
| BUG-02 `GET /api/filters` | tags sorted | insertion order | no `.sort()` call before returning |
| BUG-03 `user/update` | 400 on malformed JSON | 500 | `req.json()` throws uncaught, falls to outer 500 catch |
| BUG-04 `POST /api/dishes` | tags/allergens as arrays | raw CSV strings | schema stores `Dish.tags`/`allergens` as `String`, not `String[]` |
| BUG-05 `GET /api/allergens` | sorted fallback list | `ALLERGEN_OPTIONS` insertion order | same missing-sort pattern as BUG-02 |
| BUG-06 `GET /api/party/state` | 404 if inactive | 200, ignores `isActive` | route never checks the flag it stores |
| BUG-07 `DELETE /api/dishes/[id]` | 500 on generic DB error | 404 | all exceptions caught as "not found" |
| BUG-08 `PATCH /api/dishes/[id]` | 500 on generic DB error | 404 | same catch-all as BUG-07 |
| TC-06-01/04 favorites | single "Dinner" match | multiple elements match | test locator too loose — UI is correct, test needs `getAllByText` |
| TC-08-01 places | URL contains `maps.google.com` | `https://www.google.com/maps/place/?q=place_id:...` | stale assertion — real URL is a more specific, valid place-id deep link |
| TC-13-01 account | `updateUserDetails` returns updated name | returns stale name | `updateUserDetails` discards `prisma.user.update`'s return value and re-fetches instead — test only mocks the first call |
| TC-15-04/05, TC-18-03 party | 404/200 on party-code edge cases | inverted in each case | `party/join` and `party/state` don't consistently validate code existence/active status before responding |

**The 16th failure (`DietaryPreferencesSection.test.tsx` "shows error message
when saving fails") is genuinely order-dependent** — it fails inside the
full 492-test run but passes 6/6 when run completely alone
(`npx vitest run tests/app/account/DietaryPreferencesSection.test.tsx`).
This is real cross-file test pollution (state leaking from an earlier file
in the run), distinct in kind from the 15 deterministic failures above, and
worth its own fix separate from the 15 real product/test bugs.

### Issue 5: Four test files (21 test cases) are silently dropped by `pnpm test` — never counted as pass or fail

The prompt's own list of 90 test file names (prompts.md:1198-1287) includes
5 files that never appear anywhere in the full `pnpm test` run's output —
not in the pass list, not in the fail list, not even in the "Unhandled
Errors" section by name:

```
tests/components/FilterMenu.test.tsx     (4 test cases)
tests/components/MapWithPins.test.tsx    (5 test cases)
tests/components/PartyClient.test.tsx    (5 test cases)
tests/components/VideoPanel.test.tsx     (7 test cases)
tests/e2e/smoke.spec.ts                  (Playwright — correctly excluded via vitest.config.ts's own `exclude` list, not a bug)
```

Running the remaining 4 directly (`npx vitest run tests/components/FilterMenu.test.tsx
tests/components/MapWithPins.test.tsx tests/components/PartyClient.test.tsx
tests/components/VideoPanel.test.tsx`) shows why:

```
Error: require() of ES Module .../node_modules/parse5/dist/index.js from
.../node_modules/jsdom/lib/jsdom/browser/parser/html.js not supported.
...
Test Files  no tests
     Tests  no tests
    Errors  4 errors
```

Root cause, confirmed by reading each file: all 4 declare
`/** @vitest-environment jsdom */` at the top, overriding the project's
global `happy-dom` environment (`vitest.config.ts`'s `test.environment`).
The installed `jsdom` version still `require()`s its bundled `parse5`, but
the installed `parse5` version ships ESM-only — `ERR_REQUIRE_ESM` crashes
*collection* for exactly these 4 files, before a single `it()` inside them
ever runs.

This is a materially different (and worse) problem than the "4 unhandled
`ERR_REQUIRE_ESM` errors" the predecessor `Prompt_Notes_Sonnet_5.md` report
noted (that report's Issue 5) — that report characterized them as cosmetic
noise ("doesn't fail any test... all 476 passing tests still pass"). Cross-
checking: the full-suite run's own "Unhandled Errors" section shows exactly
4 occurrences of this same error, one per file — meaning these 4 files
*are* attempted during the full run and crash identically, but Vitest's
top-level summary (`Test Files 6 failed | 79 passed (85)`) never reflects
them at all: **85 + these 4 = 89, matching the 89 real (non-Playwright)
vitest-eligible files the prompt lists.** The reported denominator is
quietly short by 4 files and 21 test cases, with the exit code and file-list
output giving no visible signal that anything is missing — a silent gap, not
a noisy one. The affected files are exactly the component-level tests for
UC9 (Filter Meals by Allergen), UC15 (Find Nearby Restaurants), UC7 (View
Recipe Videos), and the umbrella party UI (`PartyClient`, touching several
party use cases) — real coverage that currently doesn't exist in practice
despite the files being present on disk.

---

## 3. Caught Issues (Static, Text-Only Prompts)

### Issue 6: The README's own two variable-optionality claims contradict each other (Prompt 15)
The README says "Remember to populate the keys in .env.local before running
the app" for Maps/YouTube "for full functionality" (prompts.md:210-213),
while `.env.example`'s own comment on those same variables says "External
APIs (optional; stubs are used if empty)" (prompts.md:1617). Both are pasted
in prompts.md; neither is wrong exactly, but a new engineer reading only the
README's "Third-Party APIs" section would reasonably conclude these are
required, when the repo's own config file says otherwise.

### Issue 7: A relationship modeled twice, once enforced and once not (Prompt 14)
`User.savedMeals` is a bare `String[]` (prompts.md:1868) with no schema-level
tie to `Dish.id`, while the same "user favorited a dish" relationship is
*also* modeled properly via the `Favorite` join table with real foreign keys
(prompts.md:1878-1884). Nothing in the schema stops `savedMeals` from
referencing a dish id that doesn't exist or has since been deleted — visible
directly from the pasted schema, no application code needed to confirm it.

### Issue 8: `user/update/route.ts` is a three-axis outlier among its siblings (Prompt 13)
Of the four route files pasted for Prompt 13, `app/api/user/update/route.ts`
is simultaneously the only one that (a) skips Zod validation for hand-rolled
`if` checks (prompts.md:1784,1788), (b) returns `NextResponse.json` instead
of the other three's bare `Response.json` (prompts.md:1776), and (c) uses a
bare `{error: "..."}` response envelope (prompts.md:1785) instead of the
`{code}`/`{code, message}` shape the other three converge on
(prompts.md:1728,1821). All three drifts point at the same file, suggesting
it predates whatever convention the rest of the API settled on.

---

## 4. Strengths & Weaknesses of Claude Sonnet 5 on This Task

### Strengths
1. **Held the text-only boundary under pressure.** Prompt 11 (dependency map)
   and Prompt 12 (public surface) both *invite* citing exact source lines for
   where env vars are read or auth is checked — but neither prompt pastes
   that source. Correctly declined to fabricate `lib/*.ts:LINE` citations
   for material never shown, even though the actual live repo (browsed for
   prompts 6–8) would have made those citations trivial to produce. Named
   what to paste next instead of guessing.
2. **Went past the given error text in Prompt 6 instead of transcribing it.**
   Reproduced the font-fetch failure independently, then used real network
   diagnostics (`curl` with/without `-k`) to confirm *why* it happens rather
   than just applying the hinted fix blind, then kept going through three
   more real, distinct failures once the first was fixed — arriving at a
   genuine repo-level bug (`.env.example`'s Stack Auth placeholder is
   invalid) that the pre-baked prompt text doesn't mention at all.
3. **Verified before reporting, in both directions.** For Prompt 7, ran the
   new test file against the real implementation rather than trusting that
   correctly-reasoned test code would pass. For Prompt 8, re-ran every
   reported failure in isolation before calling it real, which is what
   caught the one genuinely order-dependent failure (Issue 4) instead of
   lumping all 16 together.
4. **Found a bigger bug than the one being looked for.** The silently-
   dropped-test-files finding (Issue 5) wasn't what Prompt 8 asked for —
   it surfaced from grepping full log output for filenames rather than just
   reading the pass/fail summary line, and materially changes how much the
   "85 files, 79 passed" headline number should be trusted.

### Weaknesses
1. **The 90-file traceability table leans on `describe()`-title grepping for
   depth, not full-file reads.** For the ~70 files outside the two dedicated
   `use-cases*` directories, UC mapping in Issue 3's supporting analysis is
   based on top-level `describe()` titles and file/component names, not a
   read of every test body — reasonable for a single evaluation pass, but a
   handful of those mappings (marked `(?)` in working notes, condensed out of
   the final tables here for length) are inferred rather than confirmed, the
   same honest caveat Prompt 8 explicitly permits ("mark it '?'").
2. **Prompt 9's chosen comparison library (`pure-rand`) is asserted from
   general knowledge of the JS seeded-PRNG ecosystem, not verified against
   this repo's own dependency list** — `pure-rand` is not one of the
   packages in `package.json` (Prompt 11's pasted manifest), so the
   comparison is conceptually sound but not itself grounded in
   prompts.md's pasted material the way every other prompt's evidence is.
3. **Root-caused fewer of the 15 real test failures to actual source lines
   than the file:line standard applied elsewhere.** Issue 4's table names
   the right file and behavior for each failure (e.g. "no `.sort()` call")
   but, unlike Issue 5's parse5 root-cause or Issue 1's build chain, most of
   these weren't traced to a specific source line inside the corresponding
   route handler — a deeper pass would open each route file and cite the
   exact missing `.sort()`/`.isActive` check.
