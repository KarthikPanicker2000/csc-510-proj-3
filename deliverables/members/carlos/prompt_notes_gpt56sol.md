# Deliverable D5: Prompt Notes, Model Evaluation, & Caught Errors

## Executive Summary & Model Configuration

The fifteen prompts in `prompts.md` were evaluated against the MealSlot application in
`proj2/mealslot` using **GPT-5.6 Sol**. The evaluation used both repository inspection
and attempted execution on Windows with Node.js 20.15.0. The execution results below
separate environment failures from code and test results.

---

## 1. Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| **1: First contact with repo** | **Earned Keep** | Clearly identifies the Next.js 16 App Router application, Prisma/Neon data layer, Socket.IO server, and Vitest/Playwright testing setup. |
| **2: Module to user goals** | **Earned Keep** | Converts modules such as `dishes.ts`, `party.ts`, and `rateLimit.ts` into code-supported user goals without relying on product assumptions. |
| **3: Use case and edges** | **Earned Keep** | The fixed format and citation requirements produce reviewable use cases while distinguishing handled and unhandled failures. |
| **4: Undocumented product** | **Earned Keep** | Surfaces features that receive little README coverage, including rate limiting, saved dishes, authentication handlers, and party-state APIs. |
| **5: Fragile code areas** | **Earned Keep** | Encourages evidence-based ranking of high-change and integration-heavy areas such as the main page, party client, slot machine, maps, and external services. |
| **6: Broken build triage** | **Executed** | After a frozen hoisted install, typecheck passed and the production build reached Next.js/Turbopack but failed fetching the Bungee and Sora Google Fonts over TLS. This is a setup/network failure with high confidence, not compiler evidence of code rot. |
| **7: Tests for naked code** | **Executed** | Vitest ran 492 tests: 476 passed, 15 failed, and 1 was skipped. All five failing files reproduced standalone; source tracing distinguishes 8 real API defects from 7 defective-test failures. |
| **8: Two-way traceability** | **Executed** | Runtime evidence now connects failing use-case/regression tests to the implementing routes. Eight regression tests expose concrete behavior at cited source lines; seven other failures trace to stale assertions or mock leakage rather than product behavior. |
| **9: Then versus now** | **Use Selectively** | MealSlot already uses Next.js 16 and React 19, so the prompt needs a specifically identified legacy implementation to provide value. |
| **10: Honest rewrite** | **Earned Keep** | The identical-behavior constraint and test mapping support safer refactoring and reveal missing regression coverage. |
| **11: Dependency map** | **Earned Keep** | Found the mandatory PostgreSQL `DATABASE_URL`, optional/fallback-backed API integrations, undocumented environment-name drift, and several apparently unused declared packages. |
| **12: Public surface** | **Earned Keep** | Enumerated 19 method/path combinations across 17 route files. No handler contains an authenticated-session or permission check; user- and dish-mutating endpoints trust caller-supplied identifiers. |
| **13: Naming and pattern drift** | **Earned Keep** | Exposed concrete drift in map keys, websocket URLs, response error shapes, JSON/CSV storage, authentication identifiers, and duplicate realtime/map implementations. |
| **14: Data model reconstruction** | **Earned Keep** | Reconstructed six Prisma entities and distinguished real foreign keys from ID arrays/JSON blobs that application code must maintain. It also found unused or write-only fields and a host ID with no schema relation. |
| **15: Outside-in onboarding** | **Earned Keep** | Produces an actionable checklist but reveals that the checked-in quick start is stale: it describes SQLite despite an active PostgreSQL schema and invokes a nonexistent websocket `dev` script. |

---

## 2. Prompt x Model Verdict Table

| Category | Model Verdict | Evidence & Rationale |
|---|---|---|
| Repository overview | **CONFIRM** | `package.json` and the source tree confirm Next.js, React, TypeScript, Prisma, Neon, Socket.IO, Vitest, and Playwright. |
| Goal extraction | **CONFIRM** | The application supports meal spinning, filters, allergens, recipes, maps, favorites, accounts, and party coordination. |
| Hidden features | **CONFIRM** | Source routes and libraries expose rate limiting, saved-dish management, authentication callbacks, and party lifecycle operations. |
| Build triage | **SETUP/NETWORK FAILURE** | `pnpm typecheck` passed. `pnpm build` generated Prisma Client and began the optimized Next.js build, then failed only because TLS prevented `next/font` from downloading Bungee and Sora. |
| Test traceability | **CONFIRM WITH FAILURES** | Vitest executed 85 files and 492 tests: 80 files passed, 5 failed; 476 tests passed, 15 failed, and 1 skipped. Each failing file was rerun alone and failed deterministically. |
| Modernization | **LIMITED VALUE** | The core framework versions and application structure are already modern. |
| Dependency/config map | **CONFIRM WITH DRIFT** | The database is mandatory; Stack Auth, OpenAI, YouTube, Maps, and websocket integrations have fallbacks or degraded modes. Several documented environment names do not match code. |
| Public API authorization | **HIGH RISK** | No authorization check was found in any of the 19 route methods; `/api/dishes/[id]` and caller-ID-based user mutation routes are the highest-risk surfaces. |
| Data model integrity | **MIXED** | Prisma enforces User/Favorite/Dish and Party/PartyMember relations, but saved dish IDs, spin result dish IDs, and party hosting are not relationally enforced. |
| Onboarding documentation | **STALE/BLOCKING** | `.env.example` exists, but its SQLite URL cannot satisfy the active PostgreSQL Prisma provider, and the README invokes nonexistent `pnpm prisma ...` scripts. |

---

## 3. Caught Issues & Sanity Checks

### Issue 1: Rate limiting is process-local

`lib/rateLimit.ts` stores limiter state in memory. In a multi-instance deployment, the
limit is enforced independently by each process rather than globally.

### Issue 2: External integrations are major failure boundaries

Google Places/Maps, Neon/Prisma, authentication, recipe and video services, and
Socket.IO introduce network, configuration, quota, and timing failures that static
inspection cannot fully validate.

### Issue 3: Eight regression tests confirm real API defects

`tests/use-cases-qwen/uc-regression-bugs.test.ts` failed all eight tests both in the
full suite and standalone. The observed behavior matches the implementation:

- Empty party `memberId` is accepted because the schema uses `z.string()` without
  `.min(1)` (`app/api/party/leave/route.ts:12-14`).
- Filter tags preserve insertion order while allergens are explicitly sorted
  (`app/api/filters/route.ts:27-42`, `app/api/filters/route.ts:88`).
- Malformed JSON reaches the broad 500 handler (`app/api/user/update/route.ts:15-18`,
  `app/api/user/update/route.ts:42-47`).
- Dish creation stores and returns CSV `tags`/`allergens`, not response arrays
  (`app/api/dishes/route.ts:110-124`).
- The allergens error fallback returns the static list without sorting it
  (`app/api/allergens/route.ts:32-39`).
- Party state queries by code without `isActive: true`
  (`app/api/party/state/route.ts:39-44`).
- Dish DELETE and PATCH convert every database exception, including generic failures,
  to 404 (`app/api/dishes/[id]/route.ts:36-40`, `app/api/dishes/[id]/route.ts:67-85`).

### Issue 4: Seven deterministic failures are defects in the tests

- Three party failures are mock-queue leakage: `vi.clearAllMocks()` preserves queued
  implementations (`tests/use-cases/uc14-19-party.test.ts:171-172`), and TC-15-02
  queues a party result before validation exits without consuming it
  (`tests/use-cases/uc14-19-party.test.ts:200-207`). Later 404/success cases therefore
  receive prior queued values even when run as a file by itself.
- Two favorites failures are assertion/design mismatches. `getByText("Dinner")` is
  ambiguous because both the filter and meal card render that text
  (`tests/use-cases/uc05-07-favorites.test.tsx:219-223`), while the component only
  displays categories present in saved meals (`app/favorites/page.tsx:88-96`), so a
  Breakfast-only fixture cannot click a Dinner filter.
- The account test queues unused `findUnique` results during registration even though
  `ensureUserInDB` returns the upsert directly (`app/actions.ts:110-125`); because its
  `beforeEach` only clears call history, TC-13-01 reads the stale Alice result rather
  than its queued Jane result (`tests/use-cases/uc10-13-account.test.ts:66-79`,
  `tests/use-cases/uc10-13-account.test.ts:155-179`).
- The places route emits a valid `https://www.google.com/maps/...` URL
  (`app/api/places/route.ts:102-104`), but the test requires the different hostname
  substring `maps.google.com` (`tests/use-cases/uc08-places.test.ts:91-99`).

---

## 4. Execution Results and Build Triage

### Environment

- OS/shell: Windows PowerShell
- Node.js: `v20.15.0` (satisfies the declared `>=18.18.0` requirement)
- Declared package manager: `pnpm@10.24.0`
- Installed package manager: `pnpm 10.24.0`, installed with
  `npm install -g pnpm@10.24.0`; npm global prefix
  `C:\Users\carlo\AppData\Roaming\npm` was added to the shell `PATH`
- Dependencies: installed from the lockfile with
  `pnpm install --frozen-lockfile --node-linker=hoisted`; Prisma Client generation
  completed successfully
- Last repository commit: `e884ffdd7e3e7bf663312b3b2043e7613f87fb90`,
  dated 2025-12-08

### Commands Executed

| Command | Result | Exact cause |
|---|---|---|
| `pnpm typecheck` | **Passed (exit 0)** | `tsc -p tsconfig.json --noEmit` completed with no diagnostics. |
| `pnpm test` | **Failed (exit 1)** | 85 files: 80 passed, 5 failed. 492 tests: 476 passed, 15 failed, 1 skipped. Vitest also reported 4 unhandled `ERR_REQUIRE_ESM` errors from jsdom requiring ESM-only parse5. |
| `pnpm build` | **Failed (exit 1)** | Prisma Client generated; Turbopack failed because TLS blocked downloads of Bungee and Sora from Google Fonts. |

Complete outputs were captured in `proj2/mealslot/typecheck-gpt56sol.log`,
`proj2/mealslot/test-gpt56sol.log`, and `proj2/mealslot/build-gpt56sol.log`. The five
failing files were then run independently with `pnpm exec vitest run <file>`; each
reproduced with the same failures (3, 8, 2, 1, and 1 respectively).

### Prompt 6 Classification

- **Setup/network problem: 95% confidence.** The build's only fatal errors are
  `Failed to fetch 'Bungee' from Google Fonts` and `Failed to fetch 'Sora' from Google
  Fonts`, with Turbopack explicitly identifying TLS. `components/HeaderClient.tsx:29-33`
  declares those remote fonts.
- **Code rot: 4% confidence.** Next.js reports only non-fatal deprecations for
  `images.domains` and `experimental.typedRoutes`; typecheck passes, so no framework or
  TypeScript incompatibility was demonstrated.
- **Real build-blocking application bug: 1% confidence.** The test run does confirm
  eight API behavior defects, but none explains the production-build failure.

The app is structurally healthy enough to typecheck, generate Prisma Client, compile
into the Next.js production-build phase, and pass 476 tests. The cheapest build
experiment is enabling Turbopack system TLS certificates as the error recommends or
self-hosting the two fonts; abandoning the project is not justified.

---

## 5. Static Exploration Results for Prompts 11-15

### Prompt 11: Dependency Map

| Dependency/integration | Required to start? | Configuration and static evidence |
|---|---|---|
| Node.js, pnpm, installed packages | Yes | Node `>=18.18.0`, pnpm `10.24.0`, and the start/build scripts are declared in `package.json:5-28`. |
| PostgreSQL through Prisma | Yes for data-backed startup/use | The active datasource is `provider = "postgresql"` and reads `DATABASE_URL` (`prisma/schema.prisma:5-8`); every major route imports the Prisma singleton (`lib/db.ts:8-20`). |
| Stack Auth | No; degraded anonymous mode exists | The client reads `NEXT_PUBLIC_STACK_PROJECT_ID` and `NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY`, but substitutes a null-user stub when absent (`stack/client.ts:6-28`). |
| OpenAI | No; deterministic recipe fallback | `OPENAI_API_KEY` selects the remote branch; absence uses local stubs (`lib/llm.ts:169-182`). |
| YouTube Data API | No; stub results returned | Both implementations read `YOUTUBE_API_KEY` and handle its absence (`lib/youtube.ts:60-68`, `app/api/videos/route.ts:13-25`). |
| Google Maps/Places | No for startup; map/real venue functionality degrades | Server lookup reads `MAPS_API_KEY` (`app/api/places/helpers.ts:3-6`); clients read `NEXT_PUBLIC_GOOGLE_MAPS_KEY` (`components/MapWithPins.tsx:44-66`) or the inconsistent `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (`components/PartyMap.tsx:95-108`). |
| Realtime websocket server | No; same-origin BroadcastChannel fallback | Client code reads `NEXT_PUBLIC_WS_URL` and otherwise uses BroadcastChannel (`lib/realtime.ts:102-111`); the separate server reads `PORT` with default 4001 (`ws-server/src/index.ts:5`). |
| Google Fonts at production build time | Yes for the current build path | Bungee and Sora are build-time `next/font/google` dependencies (`components/HeaderClient.tsx:29-33`), confirmed by Prompt 6's TLS failure. |

The clearest declared-but-unreferenced dependency is `zustand`: it is declared at
`package.json:54`, but repository-wide static search found no source import. The same
search also found no source use of `bcryptjs`, `neon-js`, `next-auth`, or
`socket.io-client`; these are additional cleanup candidates, not proven safe removals
without checking generated/runtime loading behavior.

Configuration drift matters here: `.env.example:24-25` documents `WS_URL`, while the
client reads `NEXT_PUBLIC_WS_URL`; `.env.example` does not document
`NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`; and its SQLite `DATABASE_URL` example
(`.env.example:7-11`) is incompatible with the active PostgreSQL provider.

### Prompt 12: Public Surface

No route handler imports or calls `stackServerApp`, resolves the authenticated user,
or checks a role/permission. An `auth_id`, `authId`, `userId`, `memberId`, party code,
or dish ID in a request is validation/input, not proof of authorization.

| Method | Path | Purpose | Authorization/permission check |
|---|---|---|---|
| GET | `/api/allergens` | Return merged allergen choices | NONE FOUND |
| GET | `/api/dishes` | List dishes, optionally by category | NONE FOUND |
| POST | `/api/dishes` | Create a dish | NONE FOUND |
| PATCH | `/api/dishes/[id]` | Modify any identified dish | NONE FOUND |
| DELETE | `/api/dishes/[id]` | Delete any identified dish | NONE FOUND |
| GET | `/api/filters` | Aggregate dish tags and allergens | NONE FOUND |
| POST | `/api/party/create` | Create a party and host member | NONE FOUND |
| POST | `/api/party/join` | Join an active party by code | NONE FOUND |
| POST | `/api/party/leave` | Delete a party member by ID | NONE FOUND |
| POST | `/api/party/spin` | Produce a party selection | NONE FOUND |
| GET | `/api/party/state` | Read party state and members by code | NONE FOUND |
| POST | `/api/party/update` | Update member preferences and party constraints | NONE FOUND |
| POST | `/api/places` | Find restaurants for cuisines | NONE FOUND |
| POST | `/api/recipe` | Generate recipes | NONE FOUND |
| POST | `/api/spin` | Select dishes and persist a spin | NONE FOUND |
| POST | `/api/user/create` | Upsert a user from supplied `auth_id` | NONE FOUND |
| POST | `/api/user/saved` | Replace saved meals for supplied `authId` | NONE FOUND |
| POST | `/api/user/update` | Change the name for supplied `userId` | NONE FOUND |
| POST | `/api/videos` | Find or stub recipe videos | NONE FOUND |

The riskiest single route file is `/api/dishes/[id]`: unauthenticated PATCH and DELETE
perform destructive global catalog mutations solely from the URL ID
(`app/api/dishes/[id]/route.ts:30-40`, `app/api/dishes/[id]/route.ts:53-85`). The user
mutation routes are nearly tied: `/api/user/saved` trusts caller-supplied `authId`
(`app/api/user/saved/route.ts:28-47`) and `/api/user/update` trusts `userId`
(`app/api/user/update/route.ts:15-39`).

### Prompt 13: Naming and Pattern Drift

| Problem | Pattern A | Pattern B / assessment |
|---|---|---|
| Google Maps public key | `NEXT_PUBLIC_GOOGLE_MAPS_KEY` in `MapWithPins` (`components/MapWithPins.tsx:44-66`) | `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` in `PartyMap` (`components/PartyMap.tsx:95-108`). The former is documented; PartyMap is the holdout. |
| Websocket URL | Code reads `NEXT_PUBLIC_WS_URL` (`lib/realtime.ts:105-111`) | `.env.example` supplies `WS_URL` (`.env.example:24-25`). Public-prefixed name is required by client code; documentation is stale. |
| Auth identifier | Prisma and several routes use `auth_id` (`prisma/schema.prisma:13-16`, `app/api/user/create/route.ts:17-43`) | Saved-meal route calls it `authId`, while update calls the same external identifier `userId` (`app/api/user/saved/route.ts:10-40`, `app/api/user/update/route.ts:15-38`). Schema naming is the stable pattern; route names drift. |
| Error response shape | Zod routes commonly return `{ issues }`; party failures return `{ code }` (`app/api/party/join/route.ts:34-45`) | User routes return `{ error }`, saved meals returns `{ message }`, and spin mixes `code` plus `message` (`app/api/user/update/route.ts:20-47`, `app/api/spin/route.ts:150-157`). No single newer convention is evident. |
| Multi-value persistence | User allergens/saved meals are native PostgreSQL arrays (`prisma/schema.prisma:17-18`) | Dish tags/allergens are comma strings and party/spin structures are JSON strings (`prisma/schema.prisma:39-40`, `prisma/schema.prisma:55-58`, `prisma/schema.prisma:68-77`). Native arrays look newer; serialized strings are holdouts. |
| Realtime transport | README/server use Socket.IO (`README.md:134-142`, `ws-server/src/index.ts`) | Browser client implements raw WebSocket/BroadcastChannel and does not import `socket.io-client` (`lib/realtime.ts:1-10`, `lib/realtime.ts:61-111`). The lightweight client appears newer but is protocol-incompatible with Socket.IO. |
| Map implementation | `MapWithPins` dynamically injects a script and renders venue pins (`components/MapWithPins.tsx:63-153`) | `PartyMap` uses `next/script`, a global callback, and one user marker (`components/PartyMap.tsx:87-110`). Neither clearly supersedes the other; this is duplicated integration logic. |

### Prompt 14: Reconstructed Data Model

| Entity | Key fields | Relationships enforced by Prisma |
|---|---|---|
| User | `id`, unique external `auth_id`, name, `savedMeals[]`, `allergens[]` | One-to-many Favorite, PartyMember, and optional-user Spin records (`prisma/schema.prisma:13-22`). |
| Dish | String ID, category, serialized tags/allergens, cost/time bands, media/metadata | One-to-many Favorite (`prisma/schema.prisma:35-50`). |
| Favorite | `userId`, `dishId` | Required many-to-one links to User and Dish (`prisma/schema.prisma:27-33`). |
| Spin | optional `userId`, four serialized selection/configuration fields, timestamp | Optional many-to-one User; no Dish relation (`prisma/schema.prisma:52-61`). |
| Party | unique code, optional `hostId`, active flag, serialized constraints | One-to-many PartyMember only (`prisma/schema.prisma:63-71`). |
| PartyMember | required `partyId`, optional `userId`, serialized preferences, timestamp | Required Party and optional User (`prisma/schema.prisma:73-81`). |

Unused/write-only candidates found by static search:

- The `Favorite` model has no application-code queries; favorites use `User.savedMeals`
  string IDs instead (`app/actions.ts:54-68`, `app/favorites/page.tsx:64-71`).
- `Dish.cuisineType` and `Dish.keyIngredients` are written only by the seed
  (`prisma/seed.ts:112-148`) and are not read by application code.
- `Party.hostId` is neither a relation nor set by the party-create route, which creates
  only `code`, `isActive`, and constraints (`app/api/party/create/route.ts:40-47`).
- Dish timestamps and `PartyMember.joinedAt` are schema-managed but not read by current
  application code.

Application-only integrity includes `User.savedMeals[]` and `Spin.resultDishIds` as
Dish IDs without foreign keys (`prisma/schema.prisma:17`, `prisma/schema.prisma:57`),
plus an inferred live party host in component state rather than `Party.hostId`
(`components/PartyClient.tsx:205-206`). Conversely, Prisma enforces Favorite relations
that the current application bypasses entirely.

### Prompt 15: Outside-In Onboarding Checklist

| Step | What a new engineer would do | Does the repository suffice? |
|---|---|---|
| 1 | Install Node `>=18.18.0` and pnpm `10.24.0` | **Yes**, versions are in `package.json:5` and `package.json:27-28`; README's `pnpm@latest` instruction is less reproducible (`README.md:79-82`). |
| 2 | Copy `.env.example` to `.env.local` | **Yes mechanically**, but the filename command is Unix-specific and values contain contradictions (`README.md:85`, `.env.example`). |
| 3 | Choose and start PostgreSQL, then set `DATABASE_URL` | **Partly.** Docker Compose supplies Postgres credentials (`docker-compose.yml:2-13`), but README says SQLite is the default and tells the engineer to change the Prisma datasource even though it is already PostgreSQL (`README.md:107-116`, `prisma/schema.prisma:5-8`). |
| 4 | Install dependencies | **Yes**, lockfile and manifest exist. On this exFAT checkout, the required hoisted linker is tribal knowledge absent from the repo. |
| 5 | Generate Prisma Client and apply schema | **Yes, after fixing the database URL.** `postinstall` generates the client; both the README's direct Prisma CLI commands and the `prisma:push`/`prisma:seed` scripts are available (`README.md:82-85`, `package.json:18-25`). |
| 6 | Start Next.js on port 3000 | **Yes**, `pnpm dev` is defined (`package.json:7`). Basic stubbed flows can work without external API secrets. |
| 7 | Configure authentication | **Optional but incomplete.** Two public Stack variables are documented (`.env.example:5-6`) and missing values yield an anonymous stub (`stack/client.ts:6-23`); any server-side Stack credential expectations are not documented. |
| 8 | Configure Maps, YouTube, and OpenAI for full features | **Mostly.** Keys are listed and missing keys have fallbacks, but PartyMap's alternate map-key name is undocumented. Real credentials must come from outside the repo. |
| 9 | Start realtime server if needed | **Stuck on drift.** Server startup is documented, but its package has only `start`, not `dev` (`ws-server/package.json:5-9`), and documented `WS_URL` does not reach client-side `NEXT_PUBLIC_WS_URL`. Raw WebSocket client versus Socket.IO server also needs design clarification. |
| 10 | Run checks and E2E tests | **Partly.** scripts exist, but Playwright browser installation is not documented; production build also needs network/TLS access for Google Fonts. |

The new engineer can reach typecheck and stub-backed unit tests from repository content,
but a reliable running system requires correcting database instructions, the websocket
start command/configuration/protocol, and map-key naming. Real auth/API credentials remain
legitimate external blockers only for their corresponding full integrations.

---

## 6. Strengths & Weaknesses of GPT-5.6 Sol on MealSlot

### Strengths

1. Connects architecture, user goals, routes, and tests across the full stack.
2. Separates code-confirmed findings from claims requiring runtime evidence.
3. Produces concise use cases, edge analyses, and traceability notes from TypeScript.

### Weaknesses

1. The full run exposes mixed failure provenance, so prompt output must distinguish
   application defects, defective tests, and dependency/runtime errors rather than
   treating every red assertion as a product bug.
2. Four jsdom/parse5 `ERR_REQUIRE_ESM` errors remain environment/dependency-level test
   health issues even though 492 tests executed.
3. Prompt 9 is weak without a deliberately selected legacy code example.
