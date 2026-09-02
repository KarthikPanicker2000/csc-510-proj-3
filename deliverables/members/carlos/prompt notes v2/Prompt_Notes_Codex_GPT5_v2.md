# MealSlot Prompt Evaluation — Codex GPT-5 v2

## Executive Summary & Model Configuration

**Model:** Codex, based on GPT-5  
**Configuration:** repository-writing coding agent; PowerShell on Windows 10; Node.js 20.15.0; pnpm 10.24.0; no web browsing. Prompts 1–5 and 9–15 were evaluated solely from the fixed material embedded in `prompts.md`. Live repository inspection and execution were used only for Prompts 6–8, exactly as requested.

The prompt set is strongest when it supplies the relevant implementation and asks for bounded reasoning (Prompts 2, 3, 7, 10, 13, and 14). It is weakest where the requested conclusion requires evidence that the pasted input deliberately omits (especially Prompts 9, 11, and 12). The live pipeline is mixed: typecheck passes; the production build is blocked by TLS failures fetching Google fonts; and Vitest reports 15 failed assertions plus four collection errors. The new `weightedSpin` tests pass 3/3.

## Section 1: Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| 1 — First contact | **Earned Keep** | The visible architecture is a Next.js App Router UI/API (`app`, `components`), domain/integration layer (`lib`), Prisma persistence (`prisma`), a separate Socket.IO server (`ws-server`), and tests/tooling. The five highest-value next files are `package.json`, `prisma/schema.prisma`, `app/(site)/page.tsx`, `app/api/spin/route.ts`, and `lib/scoring.ts`. `assets/` is safe to ignore for engineering work this month. The pasted evidence also exposes README drift: Next 15 vs package Next 16, SQLite vs PostgreSQL, and “future” auth despite existing Stack Auth (`prompts.md:357-361`). |
| 2 — Module to user goals | **Earned Keep** | `withRateLimit` serves one observable goal: an API caller attempts a protected action and is either admitted or told to retry. Flow: identify IP → obtain bucket → refill by elapsed time → reject exhausted bucket with 429/retry delay → otherwise debit and continue. It visibly handles exhaustion at `prompts.md:422-427`. No dead functions exist in the pasted module. Important caveat: fallback IP collapses unidentified clients into one bucket (`prompts.md:407-410`). |
| 3 — Use case and edges | **Earned Keep** | UC7 actor: player; trigger: requests videos for one or more dishes; success: validate list → search each dish for “recipe” → normalize up to two videos → return results/errors. Existing extensions: malformed JSON/invalid list returns 400 (`prompts.md:519-526`); missing key returns deterministic stubs (`prompts.md:565-592`); per-dish HTTP/exception failures return partial results (`prompts.md:539-560`). Unhandled: duplicate dish names overwrite the same result key; malformed YouTube item shapes can erase a dish’s results through the catch; requests have no timeout, so the user can wait indefinitely. |
| 4 — Undocumented product | **Earned Keep** | Highest-impact hidden feature is already-present account/auth and saved-meal support, contradicting the roadmap (`prompts.md:343-346`) and evidenced by `/api/user/*` plus `app/actions.ts` (`prompts.md:629-656`); it deserves top-20 use cases. Dish administration (POST/PATCH/DELETE) and party preference updates are also hidden and deserve use cases if exposed to users/admins. Filter/allergen discovery endpoints are supporting behavior rather than standalone use cases. Exact implementation line citations cannot be produced from a route-name inventory alone. |
| 5 — Fragility from history | **Earned Keep** | (1) Main experience orchestration: `app/(site)/page.tsx` has the highest churn (25 touches). (2) Party UI: `PartyClient.tsx` has 19 touches and two last-minute test-fix commits. (3) Spin/data contract: `SlotMachine.tsx` (10), spin route (9), and Prisma schema (11) jointly form a frequently changed boundary. The evidence supports churn risk, but not TODO density or function length because those data were not pasted. |
| 6 — Broken-build triage | **Earned Keep** | Fresh live run: `pnpm typecheck` passes. `pnpm build` completes Prisma generation and reaches Next 16/Turbopack, then fails fetching Bungee and Sora from Google Fonts with TLS connection errors. Classification: **environment/setup, 95% confidence**, because failure occurs on two external HTTPS font fetches and no compile/type error appears. App code health is not perfect: typecheck is clean, but tests have deterministic failures. Suggested fixes: enable the documented system-certificate option, repair the host trust chain/proxy, or self-host the fonts to remove build-time network dependence. |
| 7 — Tests for naked code | **Earned Keep** | Added `tests/lib/scoring.codex-v2.test.ts`: happy path verifies one member per reel; edges verify empty-reel placeholder and valid-lock precedence. Assumption is explicit through test design: private `scoreDish`/`weightedChoice` are tested only through exported `weightedSpin`. Targeted run passes **1 file, 3/3 tests**. |
| 8 — Bidirectional traceability | **Earned Keep** | Live full run: **86 files collected: 81 passed, 5 failed; 495 tests: 479 passed, 15 failed, 1 skipped; 4 unhandled collection errors**. Every failing file reproduced independently. Canonical UC18 sign-in and UC19 sign-out lack behavioral proof; UC3 voting has coverage by component/integration/unit behavior despite weak naming. There are also infra/UI/admin tests outside the 20 UCs. Detailed filename mapping follows below; `?` means the name alone cannot establish behavior. |
| 9 — Then versus now | **Abandoned — insufficient fixed input** | The pasted material fully explains xmur3 + mulberry32, but supplies no current library/language implementation or evidence about its API, quality, dependencies, or migration cost. Under the text-only rule, naming and evaluating a library would import outside knowledge. Defensible conclusion from the paste alone: the old implementation is dependency-free, compact, deterministic, non-cryptographic, and already matches its stated use case (`prompts.md:1303-1360`). |
| 10 — Behavior-preserving rewrite | **Earned Keep** | A cleaner rewrite can move `loadGoogleMaps` outside the component, use typed helpers for `window.google`, early-return after cancellation/readiness checks, name the fallback constant, and extract the geolocation success callback. Behavior must retain: resolve with no key; reuse existing script; reject only script load failure; initial Raleigh marker; silent geolocation denial; cancellation guard. The supplied test names do not reveal assertions, so each claimed regression guard is **UNCOVERED from the pasted evidence** until those test bodies are supplied. |
| 11 — Dependency map | **Abandoned — insufficient fixed input** | Manifest/config prove startup commands and variable names, not where variables are read or which are fatal. Proven build/start dependencies are Node ≥18.18, pnpm 10.24, installed packages, Prisma generation, and `DATABASE_URL` for Prisma commands (`prompts.md:1508-1532`, `1856-1859`). The paste labels Google/OpenAI/YouTube APIs optional (`prompts.md:1612-1621`) and WS separately configured. It is impossible to cite code reads or prove an unused declared package from `package.json` and `.env.example` alone. |
| 12 — Public surface/auth | **Earned Keep with evidence limitation** | All 19 method/path rows are listed below. Because the fixed input contains route names but no handler bodies or middleware, every authorization cell must truthfully read **NONE FOUND IN PROVIDED INPUT**, not “unauthorized.” The riskiest surface is destructive dish mutation, especially `DELETE /api/dishes/[id]`, because the pasted surface provides no evidence of a guard. |
| 13 — Naming/pattern drift | **Earned Keep** | `auth_id` in party/create vs `authId` in user/saved vs `userId` in user/update (`prompts.md:1682-1685`, `1743-1746`, `1781-1785`); Zod + caught JSON in create/saved/dishes vs hand validation + uncaught JSON in update; `Response.json` vs `NextResponse.json`; `{issues}`, `{code}`, `{message}`, and `{error}` envelopes; whole-handler try/catch vs DB-only try/catch. The three Zod routes form the newer/common pattern; user/update is the holdout. |
| 14 — Reconstruct data model | **Earned Keep** | User 1→many Favorite, PartyMember, Spin; Dish 1→many Favorite; Party 1→many PartyMember. Favorite and PartyMember relations are FK-enforced; Spin.user is optional. `Party.hostId` has no relation, while `User.savedMeals: String[]` duplicates favorites without referential integrity. JSON/CSV fields (`reelsJson`, `lockedJson`, `powerupsJson`, `constraintsJson`, `prefsJson`, Dish tags/allergens) shift structure validation to application code. “Unused elsewhere” cannot be proven because no usage inventory was pasted. |
| 15 — Onboarding | **Earned Keep** | Checklist: install supported Node; install/use pnpm; copy `.env.example`; choose and provision the actual PostgreSQL database; set `DATABASE_URL`; install; generate/push/seed Prisma; run app; optionally run WS server and external APIs; run typecheck/tests/E2E. The repo supplies commands and placeholders, but blocks a newcomer on contradictory database guidance (README SQLite vs schema PostgreSQL), real Stack/API credentials for full functionality, and absent Windows/exFAT guidance. Deleted contributing/setup docs worsen the gap (`prompts.md:1948-1952`). |

## Prompt 8 Traceability Table

Mappings are based on the live run plus test names. A `?` deliberately avoids inventing coverage where a filename is insufficient.

| Test file | Canonical use case(s) | What it proves from name/live result |
|---|---|---|
| `tests/app/(site)/SitePage.test.tsx` | UC1, UC9, UC11 | Main spin page wiring; exact assertions require body review. |
| `tests/app/(site)/party/PartyPage.test.tsx` | UC2, UC4, UC16–17, UC20 | Party page wiring; exact split is unclear. |
| `tests/app/account/AccountPage.test.tsx` | UC6, UC10 | Account page behavior. |
| `tests/app/account/DietaryPreferencesSection.test.tsx` | UC2/UC9 | Preference/allergen editing. |
| `tests/app/api/allergens/allergens.route.test.ts` | UC9 | Allergen endpoint contract. |
| `tests/app/api/dishes/dishes.id.route.test.ts` | None | Dish-admin item CRUD, outside canonical 20. |
| `tests/app/api/dishes/dishes.route.test.ts` | None/UC1 support | Dish catalog CRUD/infrastructure. |
| `tests/app/api/filters/filters.route.test.ts` | UC9/UC1 support | Available filter contract. |
| `tests/app/api/party/party.routes.unit.test.ts` | UC2, UC4, UC14, UC16–17 | Party route contracts. |
| `tests/app/api/places/helpers.test.ts` | UC15 | Places helper behavior. |
| `tests/app/api/places/places.route.test.ts` | UC15 | Restaurant endpoint behavior. |
| `tests/app/api/recipe/recipe.route.test.ts` | None | Recipe generation is outside canonical 20. |
| `tests/app/api/routes.test.ts` | ? | Generic route smoke; bodies needed. |
| `tests/app/api/spin/spin.route.test.ts` | UC1, UC5, UC9, UC11 | Solo spin route behavior. |
| `tests/app/api/user/create/user.create.test.ts` | UC10 | User creation. |
| `tests/app/api/user/saved/saved.route.test.ts` | UC8, UC12–13 | Saved-meal persistence. |
| `tests/app/api/user/update/update.route.test.ts` | UC6 | Profile update route. |
| `tests/app/api/videos/videos.route.test.ts` | UC7 | Video endpoint behavior. |
| `tests/app/auth/callback/AuthPage.test.tsx` | ? UC18 support | Callback page rendering is not proof of sign-in. |
| `tests/app/context/UserContext.test.tsx` | UC6, UC8, UC10 support | User-state infrastructure. |
| `tests/app/favorites/FavoritesPage.test.tsx` | UC12–13 | Favorites page behavior. |
| `tests/app/handler/[...stack]/HandlerPage.test.tsx` | ? UC18 support | Auth handler rendering is not a sign-in assertion. |
| `tests/app/layout.test.tsx` | None | Layout infrastructure. |
| `tests/app/loading.test.tsx` | None | Loading UI. |
| `tests/components/ChatPanel.test.tsx` | UC20 | Party chat UI. |
| `tests/components/ClientMount.test.tsx` | None | Client-mount infrastructure. |
| `tests/components/DishCountInput.test.tsx` | UC1 | Spin dish-count control. |
| `tests/components/FilterMenu.test.tsx` | UC9 | Filter UI; did not collect due jsdom/parse5 error. |
| `tests/components/HeaderClient.test.tsx` | ? | Header behavior; exact UC unclear. |
| `tests/components/HeaderServer.test.tsx` | None/? | Header/server integration. |
| `tests/components/InviteBar.test.tsx` | UC17 | Invite code sharing/join support. |
| `tests/components/MapWithPins.test.tsx` | UC15 | Map UI; did not collect due jsdom/parse5 error. |
| `tests/components/Modal.test.tsx` | None | Generic UI primitive. |
| `tests/components/PartyChat.test.tsx` | UC20 | Party chat behavior. |
| `tests/components/PartyClient.test.tsx` | UC2, UC4, UC14, UC16–17, UC20 | Party client integration; did not collect due jsdom/parse5 error. |
| `tests/components/PartyMap.test.tsx` | UC15 | Party map integration. |
| `tests/components/PlacesMapCard.test.tsx` | UC15 | Places map card/geolocation behavior. |
| `tests/components/PowerUps.test.tsx` | UC11 | Power-up controls. |
| `tests/components/RecipePanel.test.tsx` | None | Recipe UI outside canonical 20. |
| `tests/components/SlotMachine.test.tsx` | UC1, UC5, UC9, UC11 | Slot-machine interaction. |
| `tests/components/SlotReel.test.tsx` | UC1, UC5 | Reel display/lock support. |
| `tests/components/SpinResult.test.tsx` | UC1, UC3, UC8 | Result display/action support. |
| `tests/components/StackWrapper.test.tsx` | ? UC18/19 support | Auth provider infrastructure, not sign-in/out behavior. |
| `tests/components/ThemeToggle.test.tsx` | None | Theme is outside canonical 20. |
| `tests/components/Toast.test.tsx` | None | Generic feedback UI. |
| `tests/components/UserMenu.test.tsx` | ? UC19 support | Filename alone does not prove the sign-out action is invoked. |
| `tests/components/VideoPanel.test.tsx` | UC7 | Video UI; did not collect due jsdom/parse5 error. |
| `tests/components/party/PartyChat.test.tsx` | UC20 | Party chat UI. |
| `tests/components/party/PartyMap.test.tsx` | UC15 | Party map UI. |
| `tests/components/party/PartySidebar.test.tsx` | UC2, UC14, UC17 | Party membership/preferences UI. |
| `tests/components/party/PartySpinMachine.test.tsx` | UC3–5 | Party spin, vote, and lock controls. |
| `tests/components/partyPage.test.tsx` | UC2, UC4, UC16–17, UC20 | Party page composition. |
| `tests/components/ui/Card.test.tsx` | None | Generic UI primitive. |
| `tests/components/ui/Ribbon.test.tsx` | None | Generic UI primitive. |
| `tests/e2e/smoke.spec.ts` | ? | Playwright smoke test; excluded from `pnpm test`. |
| `tests/integration/party/party.integration.test.ts` | UC2–4, UC14, UC16–17, UC20 | Integrated party behavior, including voting. |
| `tests/lib/allergens.test.ts` | UC9 support | Allergen utility. |
| `tests/lib/auth.test.ts` | ? UC18/19 support | Auth utility, not necessarily user behavior. |
| `tests/lib/dishes.test.ts` | UC1, UC9 support | Dish selection/filter data. |
| `tests/lib/llm.test.ts` | None | Recipe generation outside canonical 20. |
| `tests/lib/neon.test.ts` | None | Database infrastructure. |
| `tests/lib/party.test.ts` | UC2, UC16–17 support | Party domain utilities. |
| `tests/lib/rateLimit.test.ts` | UC1/UC4 support | Request throttling, not a standalone UC. |
| `tests/lib/realtime.test.ts` | UC4, UC20 support | Party realtime infrastructure. |
| `tests/lib/rng.test.ts` | UC1, UC4, UC11 support | Deterministic selection infrastructure. |
| `tests/lib/youtube.test.ts` | UC7 | Video fallback/helper behavior. |
| `tests/unit/UserContext.test.tsx` | UC6, UC8, UC10 support | User context behavior. |
| `tests/unit/actions.test.ts` | UC6, UC10 | User actions. |
| `tests/unit/apiRoutes.test.ts` | ? | Generic API smoke; bodies needed. |
| `tests/unit/mergeConstraints.test.ts` | UC2 | Party constraint merging. |
| `tests/unit/party/party.unit.test.ts` | UC2–4, UC14, UC16–17, UC20 | Party domain rules, including vote eligibility. |
| `tests/unit/recipeSchema.test.ts` | None | Recipe schema outside canonical 20. |
| `tests/unit/spinEdgeCases.test.ts` | UC1, UC5, UC9, UC11 | Spin edge behavior. |
| `tests/unit/spinLogic.test.ts` | UC1, UC5, UC11 | Spin selection logic. |
| `tests/use-cases-qwen/uc-regression-bugs.test.ts` | Mixed/supporting | Eight regression assertions; all eight fail deterministically. |
| `tests/use-cases-qwen/uc01-02-03-party-crud.test.ts` | UC17, UC16, UC14 | Join/create/leave despite local numbering. |
| `tests/use-cases-qwen/uc04-05-06-spin-prefs-state.test.ts` | UC4, UC2, party infrastructure | Party spin/preferences/state. |
| `tests/use-cases-qwen/uc07-search-restaurants.test.ts` | UC15 | Restaurant search. |
| `tests/use-cases-qwen/uc08-09-recipe-video.test.ts` | None, UC7 | Recipe generation plus videos. |
| `tests/use-cases-qwen/uc10-11-filters-allergens.test.ts` | UC9 | Filtering/allergens. |
| `tests/use-cases-qwen/uc12-13-user.test.ts` | UC8, UC6 | Save meal/update profile. |
| `tests/use-cases-qwen/uc15-17-18-dishes-party-members.test.ts` | None/? | Dish details/tags and party roster are not canonical named UCs. |
| `tests/use-cases/uc01-03-04-spin.test.ts` | UC1, UC9, UC11 | Solo spin, filters, power-ups; local numbers drift. |
| `tests/use-cases/uc02-lock-respin.test.ts` | UC5 | Lock and re-spin. |
| `tests/use-cases/uc05-07-favorites.test.tsx` | UC8, UC12–13 | Favorites flows; two assertions fail deterministically. |
| `tests/use-cases/uc08-places.test.ts` | UC15 | Places flow; one stale/incorrect URL assertion fails. |
| `tests/use-cases/uc09-videos.test.ts` | UC7 | Video flow. |
| `tests/use-cases/uc10-13-account.test.ts` | UC10, UC6 | Account registration/update; one assertion fails deterministically. |
| `tests/use-cases/uc14-19-party.test.ts` | UC16–17, UC2, UC4, UC14 | Party flows; three assertions fail deterministically. |
| `tests/use-cases/uc20-theme.test.tsx` | None | Theme toggling is a canonical-list orphan. |

**Use-case orphans:** UC18 Sign In and UC19 Sign Out have support/rendering tests but no demonstrated behavioral test.  
**Test orphans:** generic UI/layout/loading infrastructure, database helpers, recipe generation, dish administration, and theme tests do not map to the canonical 20. They are still legitimate tests; the traceability model simply lacks corresponding use cases.

## Prompt 12 Public Surface

The fixed input supplies no handler bodies or middleware for this prompt, so “NONE FOUND” means “not present in the supplied evidence,” not a confirmed vulnerability.

| Method | Path | Purpose | Authorization evidence |
|---|---|---|---|
| GET | `/api/allergens` | List allergens | NONE FOUND IN PROVIDED INPUT |
| GET | `/api/dishes` | List dishes | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/dishes` | Create dish | NONE FOUND IN PROVIDED INPUT |
| DELETE | `/api/dishes/[id]` | Delete dish | NONE FOUND IN PROVIDED INPUT |
| PATCH | `/api/dishes/[id]` | Update dish | NONE FOUND IN PROVIDED INPUT |
| GET | `/api/filters` | List filters | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/party/create` | Create party | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/party/join` | Join party | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/party/leave` | Leave party | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/party/spin` | Spin for party | NONE FOUND IN PROVIDED INPUT |
| GET | `/api/party/state` | Read party state | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/party/update` | Update party/preferences | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/places` | Find venues | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/recipe` | Generate recipe | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/spin` | Spin for meal | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/user/create` | Create/sync user | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/user/saved` | Update saved meals | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/user/update` | Update user profile | NONE FOUND IN PROVIDED INPUT |
| POST | `/api/videos` | Find recipe videos | NONE FOUND IN PROVIDED INPUT |

**Riskiest:** `DELETE /api/dishes/[id]`, because it is destructive and no authorization check is visible in the evidence.

## Caught Issues

### 1. Four test files fail before collection

`FilterMenu`, `MapWithPins`, `PartyClient`, and `VideoPanel` select jsdom while the project default is happy-dom (`proj2/mealslot/vitest.config.ts:12`). The live run emits four `ERR_REQUIRE_ESM` errors because jsdom requires ESM-only `parse5`. These tests are absent from the collected-file/test totals, so **86 files / 495 tests is not the full intended suite**.

### 2. Eight regression defects reproduce standalone

- Empty party member IDs pass validation because `memberId` is only `z.string()` (`proj2/mealslot/app/api/party/leave/route.ts:13`).
- Filters sort allergens but not tags (`proj2/mealslot/app/api/filters/route.ts:88`; response is built immediately afterward).
- Malformed JSON becomes 500 because `req.json()` is uncaught inside the outer catch (`proj2/mealslot/app/api/user/update/route.ts:17`, `:42`).
- Dish creation returns the database representation for CSV-backed tags/allergens rather than the API’s array representation (live BUG-04 assertion).
- Allergen DB-error fallback returns unsorted `ALLERGEN_OPTIONS` (`proj2/mealslot/app/api/allergens/route.ts:32-37`).
- Party state returns `isActive` but never rejects an inactive party (`proj2/mealslot/app/api/party/state/route.ts:55`).
- Dish DELETE and PATCH collapse generic database exceptions into 404 through broad catches (`proj2/mealslot/app/api/dishes/[id]/route.ts:39`, `:84`).

### 3. Seven additional use-case assertions fail deterministically

The favorites file has two brittle text-query failures; the places test expects `maps.google.com` while the implementation emits a valid `www.google.com/maps/place` URL; `updateUserDetails` returns a separately re-fetched stale mock value; and three party join/state expectations disagree with actual inactive/missing-party behavior. Each of the five failing files was rerun alone and reproduced, so none of these 15 failures can be dismissed as order-only flakiness in this run.

### 4. README and executable configuration disagree

The README claims Next.js 15 and SQLite by default, while the pasted package manifest specifies Next 16.0.7 and the Prisma schema hardcodes PostgreSQL (`prompts.md:357-359`, `1547`, `1856-1859`). It also calls login future work despite the visible Stack Auth surface (`prompts.md:343-346`, `137-140`).

### 5. The persistence model duplicates favorites without integrity

`User.savedMeals` is an unconstrained string array while `Favorite` models the same user↔dish relationship with foreign keys (`prompts.md:1868`, `1878-1884`). Stale or nonexistent saved dish IDs are schema-valid.

### 6. The production build depends on network-fetched fonts

The live build reaches Turbopack but cannot fetch Bungee and Sora over TLS. Typecheck passes, so this is not code rot; nevertheless, a production build is unnecessarily coupled to Google Fonts availability/certificate configuration through `components/HeaderClient.tsx`’s import chain.

## Strengths & Weaknesses

### Strengths

1. Strictly maintained the fixed-input boundary, including refusing to manufacture dependency usage, authorization checks, or a “modern” RNG comparison that the pasted evidence cannot support.
2. Distinguished setup/build failure from application health using independent typecheck, test, and build results.
3. Added and executed a real Prompt 7 artifact instead of merely proposing tests.
4. Re-ran every failing test file independently and separated failed assertions from collection failures.
5. Marked uncertain traceability mappings `?` rather than treating filenames as proof.

### Weaknesses

1. Many Prompt 8 mappings remain filename-level inferences; reading all test bodies would be required to prove each mapping at assertion granularity.
2. Prompt 10’s behavior-preserving rewrite is evaluated structurally rather than committed, because the overall deliverable asks for a report and the pasted-only rule bars validating a live rewrite.
3. Prompts 4 and 12 ask for implementation-level proof while supplying only route/function inventories; the report can identify evidence gaps but cannot produce honest handler-line citations.
4. The full-suite count includes pre-existing untracked tests in the shared worktree, so it describes this exact workspace state rather than a clean checkout.

## Execution Record

- `pnpm install --frozen-lockfile --node-linker=hoisted`: passed; Prisma client generated.
- `pnpm typecheck`: passed.
- `pnpm test`: failed — 81/86 files passed; 479/495 tests passed; 15 failed; 1 skipped; 4 collection errors.
- `pnpm build`: failed — Google Font TLS fetches for Bungee and Sora.
- `npx vitest run tests/lib/scoring.codex-v2.test.ts`: passed — 3/3 tests.
- Each of the five failing suite files rerun separately: all failed again.

