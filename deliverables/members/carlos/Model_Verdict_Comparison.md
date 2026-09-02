# Prompt × Model Verdict Comparison

Source reports: [Gemini_Prompt_Notes.md](Gemini_Prompt_Notes.md) (Gemini 3.6 Flash,
Medium), [Prompt_Notes_Sonnet_5.md](Prompt_Notes_Sonnet_5.md) (Claude Sonnet 5),
[prompt_notes_gpt56sol.md](prompt_notes_gpt56sol.md) (GPT-5.6 Sol) — all three run
against the same [prompts.md](prompts.md) (15 prompts) on the MealSlot codebase
(`proj2/mealslot`). A fourth run, **qwen3:8b served locally via Ollama**, is covered
separately in §4 — it has no source file (output was pasted directly into the working
session) and isn't run through the same pipeline as the other three, so it's kept out
of the main table and scorecard rather than force-fit into a fourth column.

**Method for this comparison:** every disagreement below was checked against the live
repository (grep, direct file reads, or a fresh `pnpm test`/`pnpm build` run) rather
than settled by majority vote. Two models agreeing is corroborating evidence, not proof
— see Prompt 12, where two-out-of-three would have been wrong.

---

## 1. Summary table

| # | Prompt | Gemini | Sonnet 5 | GPT-5.6 Sol | Agreement |
|---|---|---|---|---|---|
| 1 | First contact | Earned Keep | Earned Keep | Earned Keep | Agree |
| 2 | Module → user goals | Earned Keep | Earned Keep | Earned Keep | Agree |
| 3 | Use case + edges | Earned Keep | Earned Keep (partial) | Earned Keep | Agree (Sonnet hedged on unverified edges) |
| 4 | Undocumented product | Earned Keep | Earned Keep | Earned Keep | Agree |
| 5 | Rotten/fragile areas | Earned Keep | Earned Keep | Earned Keep | Agree on verdict; **disagree on which files** (see §2.1) |
| 6 | Triage broken build | Earned Keep — claims install + `prisma generate` resolved it, **no build failure reported** | Earned Keep — real `next build` TLS/Google Fonts failure, classified (b) my setup | Earned Keep — **identical** TLS/Google Fonts failure, same classification | **Disagree** — resolved for Sonnet/GPT-5.6 Sol (§2.2) |
| 7 | Tests for naked code | Earned Keep — "73 test files, 390 tests, 387 passed, 3 skipped" | Earned Keep — 85 files, 492 tests, 476 passed, 15 failed, 1 skipped (live run) | Earned Keep — **identical** 85/492/476/15/1 (live run) | **Disagree** — resolved (§2.3) |
| 8 | Two-way traceability | Earned Keep — "30-test to 20-use-case matrix," all 20 covered | Earned Keep — found UC-numbering mismatch between test labels and canonical doc | Earned Keep — traced 8 failures to real defects, 7 to test bugs, with root causes | **Disagree** — resolved (§2.3, §2.4) |
| 9 | Then vs now | Abandoned | Abandoned | Use Selectively (same substance, different label) | Agree |
| 10 | Honest rewrite | Earned Keep | Earned Keep | Earned Keep | Agree |
| 11 | Dependency map | Earned Keep — DATABASE_URL "read in `lib/db.ts` line 4" | Earned Keep — DATABASE_URL read in `lib/neon.ts:15` | Earned Keep — DATABASE_URL read via `prisma/schema.prisma:5-8` | **Disagree** — resolved (§2.5) |
| 12 | Public surface | Earned Keep — 17 routes, but several methods wrong | Earned Keep — said 16 route files | Earned Keep — 17 route files, 19 method/path combos | **Disagree** — resolved (§2.6) |
| 13 | Naming/pattern drift | Earned Keep | Earned Keep | Earned Keep | Agree on existence of drift; different examples, all independently verifiable |
| 14 | Data model reconstructed | Earned Keep — flags `Favorite` model as dead | Earned Keep — **did not** flag `Favorite` model | Earned Keep — flags `Favorite` model as dead | **Disagree** — resolved (§2.7) |
| 15 | Onboarding from outside | Earned Keep — SQLite/Postgres conflict **not caught**, all steps marked YES | Earned Keep — caught SQLite/Postgres schema conflict | Earned Keep — caught the same conflict, **plus** a `ws-server` missing-script blocker | **Disagree** — resolved (§2.8) |

---

## 2. Disagreements, resolved

### 2.1 Prompt 5 — which files are "most fragile"
Gemini named integration points (Google Maps callback timing, Socket.IO drops, Neon
cold starts) with no churn data behind them. Sonnet used `git log --stat` churn counts:
[app/(site)/page.tsx](proj2/mealslot/app/(site)/page.tsx) (25 touches),
[components/PartyClient.tsx](proj2/mealslot/components/PartyClient.tsx) (19),
[components/SlotMachine.tsx](proj2/mealslot/components/SlotMachine.tsx) (10).
**Believed: Sonnet.** Prompt 5 explicitly says "do not use folklore about this
product — only the evidence below" (churn, age, TODO density). Gemini's answer is
plausible-sounding domain reasoning, not evidence from the stated inputs. Re-ran
`git log --pretty=format: --name-only | sort | uniq -c | sort -rn` this session
— the churn numbers match Sonnet's exactly.

### 2.2 Prompt 6 — did the build actually fail?
Gemini's report states the build was "resolved" via `pnpm install` +
`prisma generate`, with no mention of `next build` failing. Sonnet and GPT-5.6 Sol both
report a full production build attempt that fails at the same point with the same
error: Turbopack can't reach `fonts.googleapis.com` to fetch the `Bungee` and `Sora`
`next/font/google` fonts, TLS-related.
**Believed: Sonnet + GPT-5.6 Sol.** Independently reproduced, byte-identical error
text and stack trace, in two separate sessions this project. `prisma generate`
succeeding is a necessary but far short of sufficient condition for "the build
resolved" — it's step one of `pnpm build`, not the whole command. Gemini's claim reads
as declaring victory at the wrong checkpoint, not as having actually run `next build`
to completion (success or failure).

### 2.3 Prompt 7/8 — test suite size and pass/fail counts
Gemini: 73 test files, 390 tests, 387 passed, 3 skipped, 12.85s.
Sonnet and GPT-5.6 Sol (independently, this session): **85 files, 492 tests, 476
passed, 15 failed, 1 skipped**, ~56s — matching to the digit.
**Believed: Sonnet + GPT-5.6 Sol, for current repo state.** Confirmed by running
`pnpm test` live in this conversation. The gap (73→85 files, 390→492 tests)
is too large to be flakiness; the most likely explanation is that Gemini's pass predates
the `tests/use-cases-qwen/` directory (8 files, including the deliberately-seeded
`uc-regression-bugs.test.ts`) being added to the repo — those files alone account for
most of the difference. This isn't necessarily a Gemini error so much as a stale
snapshot; either way, for anyone reading these reports today, the 492-test number is
the one that matches the code on disk.

### 2.4 Prompt 8 — root cause of the `TC-13-01` ("Jane Doe" vs "Alice Smith") failure
This is the sharpest three-way split, and the Sonnet report was the one that got it wrong.
- **Sonnet's original claim:** `updateUserDetails` (`app/actions.ts:75-97`) discards
  `prisma.user.update()`'s return value and instead returns a fresh `getUserDetails()`
  read; "the test only mocks `prisma.user.update`... so the second, unmocked read
  returns stale data."
- **GPT-5.6 Sol's claim:** the test's `findUnique` mock *is* set up correctly
  (`mockResolvedValueOnce(updatedUser)`), but two earlier tests in the same file
  (`TC-10-01`, `TC-10-03`, in the `UC-10` describe block) each queue an *unconsumed*
  `userFindUniqueMock.mockResolvedValueOnce(...)` — because `ensureUserInDB` (which
  those tests exercise) never actually calls `findUnique`, only `upsert`. Since the
  file's `beforeEach` calls `vi.clearAllMocks()` (which clears call history, not the
  queued `mockResolvedValueOnce` implementation queue), those two leftover "Alice
  Smith" queue entries are still sitting in front of `TC-13-01`'s own queued "Jane Doe"
  value when `TC-13-01` runs later in the same file.

Verified directly by reading [tests/use-cases/uc10-13-account.test.ts](proj2/mealslot/tests/use-cases/uc10-13-account.test.ts)
lines 1-180 and [app/actions.ts:102-130](proj2/mealslot/app/actions.ts#L102-L130).
`ensureUserInDB` (lines 102-130) calls `prisma.user.upsert` only — it never touches
`findUnique`. `TC-10-01` (line 78) and `TC-10-03` (line 127) each queue an unconsumed
`findUniqueMock.mockResolvedValueOnce(...)`. `TC-13-01` (line 168) *does* correctly
queue its own `findUnique` mock with `name: "Jane Doe"` — Sonnet's original claim that
this read was "unmocked" is factually wrong.
**Believed: GPT-5.6 Sol.** The mechanism it describes is exactly what the code and test
file show; Sonnet's original explanation correctly identified the redundant re-fetch in
production code (that part still stands, and is a real inefficiency worth fixing) but
was wrong about why the *test* fails. Filed as a correction, not a footnote.

### 2.5 Prompt 11 — where is `DATABASE_URL` actually read?
Gemini: "Read in `lib/db.ts` (line 4)." [lib/db.ts](proj2/mealslot/lib/db.ts) was read
in full this session — it never references `process.env.DATABASE_URL` anywhere; line 4
is a doc-comment. Sonnet cited [lib/neon.ts:15](proj2/mealslot/lib/neon.ts#L15).
GPT-5.6 Sol cited `prisma/schema.prisma:5-8` (`env("DATABASE_URL")`) and separately,
correctly, cited `lib/db.ts:8-20` only for "every route imports the Prisma singleton"
— a different and accurate claim that doesn't overlap with Gemini's error.
**Believed: Sonnet / GPT-5.6 Sol.** Gemini's citation is a hallucinated line reference
— `grep -n "DATABASE_URL" lib/db.ts` returns nothing.

### 2.6 Prompt 12 — how many routes, and with which HTTP methods?
Grepped every `app/api/**/route.ts` file for `^export` this session to settle this
directly:

| Route | Gemini claims | Actual (verified) |
|---|---|---|
| `/api/dishes/[id]` | `GET` | `DELETE`, `PATCH` — **no `GET` exists** |
| `/api/user/saved` | `GET`, `POST`, `DELETE` | `POST` only — **`GET`/`DELETE` don't exist** |
| `/api/places` | `GET` | `POST` |
| `/api/videos` | `GET` | `POST` |

Gemini fabricated HTTP methods on 4 of ~17 route files — two phantom methods added
outright (`GET /api/dishes/[id]`, `GET`+`DELETE /api/user/saved`), two swapped
(`GET`→`POST` on places and videos). Sonnet and GPT-5.6 Sol both correctly show `POST`
for places/videos; GPT-5.6 Sol's full method table (17 files, 19 method/path combos)
matches the grep above exactly.
Separately: **Sonnet's own report undercounted**, saying "16 route files." Recounting
Sonnet's own enumerated file list gives 17, matching GPT-5.6 Sol. Correction filed
against Sonnet here too.
**Believed: GPT-5.6 Sol's table, verbatim.** It's the only one of the three that is
fully correct on both file count and every individual method.

### 2.7 Prompt 14 — is the `Favorite` Prisma model actually used?
Gemini and GPT-5.6 Sol both independently flag `Favorite` (the relational join table
with `userId`/`dishId` foreign keys) as dead — favorites are actually persisted via
`User.savedMeals: String[]` instead. **Sonnet's report never mentions this at all.**
Checked fresh this session: `grep -rn "prisma\.favorite\|\.favorites\b" app lib
components` (excluding tests) returns zero hits.
**Believed: Gemini + GPT-5.6 Sol; Sonnet incomplete.** This is a real, verifiable gem
that two of three models found and one missed — worth calling out plainly rather than
folding into the "agreement" column, since it's genuinely useful information
(`Favorite` plus its migration is safe to drop or needs to be wired up).

### 2.8 Prompt 15 — is the onboarding checklist actually clean?
Gemini marks every onboarding step "YES" / provided by the repo, including the
database step, based on `.env.example`'s `DATABASE_URL="file:./dev.db"` looking like a
complete SQLite default. Sonnet and GPT-5.6 Sol both independently catch that
[prisma/schema.prisma:6](proj2/mealslot/prisma/schema.prisma#L6) hardcodes
`provider = "postgresql"`, so that documented SQLite default cannot actually work —
verified by reading the schema file directly earlier in this session.
GPT-5.6 Sol additionally catches something neither Gemini nor Sonnet found: the
README tells a new engineer to run `cd ws-server && pnpm install && pnpm dev`, but
[ws-server/package.json](proj2/mealslot/ws-server/package.json) only defines a
`start` script — no `dev` script exists. Verified by reading the file directly:
running the documented command would fail with "Missing script: dev."
**Believed: GPT-5.6 Sol's version of this checklist.** It's a strict superset of
Sonnet's finding and catches one more real, independently-verified blocker that the
other two missed entirely.

---

## 3. Scorecard

| | Unique correct findings (verified, not duplicated elsewhere) | Verified errors this session |
|---|---|---|
| **Gemini** | — | Claimed build "resolved" with no `next build` attempt; test counts stale (390 vs. 492); 4 hallucinated/wrong HTTP methods; wrong `DATABASE_URL` citation; missed the Postgres/SQLite onboarding conflict |
| **Sonnet 5** | UC-numbering mismatch (test labels vs. canonical `usecasestop20.md`) | Missed the dead `Favorite` model (caught by both others); wrong mechanism for `TC-13-01` (right symptom, wrong cause); undercounted routes (16 vs. 17) |
| **GPT-5.6 Sol** | `ws-server` missing `dev` script; correct `TC-13-01` mock-queue-leakage mechanism; fully correct route/method table | None found this session |

The pattern worth naming: **the two reports produced by models that actually executed
the build/test pipeline this session (Sonnet, GPT-5.6 Sol) agree with each other almost
everywhere they overlap, digit-for-digit on test counts and byte-for-byte on the build
error.** Where Gemini disagrees with both, live re-verification sided with the
executed pair every time. Where Sonnet and GPT-5.6 Sol disagree with each other
(§2.4, §2.6, §2.7), it wasn't 2-vs-1 — it was two static-analysis claims that needed a
tiebreaking read of the actual source, and GPT-5.6 Sol's static analysis was more
carefully sourced in every case checked.

---

## 4. A fourth data point: qwen3:8b (local, non-comparable)

**Configuration:** qwen3:8b served locally through Ollama, thinking disabled, 24,576
token context window, temperature 0.25. Source files were supplied with line numbers
prepended for citation-checking. No tool use, no `git`/`pnpm` execution, no separate
report file — one-shot text generation against pre-supplied source, pasted directly
into this session.

**Why it isn't in the table above:** the other three reports came from full agentic
sessions — reading files, running `git log`, executing `pnpm test`/`pnpm build`,
grepping the live tree — over an entire repo. qwen3:8b's run was a single-pass text
completion over whatever source text was pasted into its context window, scored by a
separate automated pipeline that itself reports "Evaluation pass failed to parse" for
most prompts. That's a different task shape, not a weaker attempt at the same one, so
scoring it against Gemini/Sonnet/GPT-5.6 Sol on the same axis would misrepresent both.

**What actually happened:** 9 of 15 prompts were attempted (2, 3, 6, 7, 9, 10 not run
— consistent with the ones needing either a pasted module/use-case format the harness
didn't supply, or real execution, which this configuration never attempted). Of those
9, 6 came back "Abandoned — evaluation pass failed to parse." Only Prompt 5 (fragile
areas) and Prompt 15 (onboarding) produced usable output; Prompt 13 was partially
salvaged from malformed output. Prompt 2's "Caught Issues" section and the
Strengths/Weaknesses section were both empty.

**Verification of the one falsifiable claim it made:** Prompt 5's output cited three
files as large — `llm.ts:287`, `route.ts:214`, `PartySpinMachine.tsx:385` — and its own
self-reported citation audit claimed 3 of 3 resolved. Checked directly this session:

| Citation | Actual line count |
|---|---|
| `lib/llm.ts:287` | 287 lines total — **matches exactly** |
| `route.ts:214` | `app/api/party/spin/route.ts` is 214 lines — the largest `route.ts` in the repo, **matches exactly** |
| `PartySpinMachine.tsx:385` | `components/party/PartySpinMachine.tsx` is 385 lines total — **matches exactly** |

All three check out — qwen3:8b's citation-audit claim was accurate, not hallucinated.
The catch: each citation is just the file's final line number, i.e., "this file is
long." There's no churn, TODO density, function-size, or age evidence behind it the
way Prompt 5 asks for — accurate, but shallow enough that it barely clears the bar of
"a finding."

**Read on this run:** not evidence that 8B-class local models can't do this task —
evidence that *this specific configuration* mostly couldn't. `thinking disabled` is the
biggest suspect: Qwen3 is a hybrid reasoner built to use a chain-of-thought pass on
exactly this kind of multi-step structured task (read code → cite a line → classify →
write a row), and running it thinking-off is closer to asking a reasoning model to
skip its main mechanism. Before concluding 8B is a hard floor for this task locally,
the cheapest next experiment is the same model, same hardware, thinking enabled.
