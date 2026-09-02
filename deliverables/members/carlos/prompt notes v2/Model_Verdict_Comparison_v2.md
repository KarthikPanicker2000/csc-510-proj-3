# Prompt × Model Verdict Comparison — v2 (Controlled Input)

Source reports: [Prompt_Notes_Claude_v2.md](Prompt_Notes_Claude_v2.md) (Claude
Sonnet 5), [Prompt_Notes_Gemini_v2.md](Prompt_Notes_Gemini_v2.md) (Gemini 3.6
Flash, Medium), [Prompt_Notes_Codex_GPT5_v2.md](Prompt_Notes_Codex_GPT5_v2.md)
(Codex, GPT-5) — all three run against the *fully instantiated*
[prompts.md](prompts.md) under the same two-track rule: prompts 1–5 and 9–15
answered from pasted content only, prompts 6–8 answered by actually running
`proj2/mealslot`. This supersedes the v1 comparison in
[Model_Verdict_Comparison.md](Model_Verdict_Comparison.md), which compared
three reports that each had open repo access throughout and self-selected
different inputs for several prompts.

**Before the per-prompt comparison, one finding that qualifies everything
below:** this was not three isolated clean checkouts.

---

## 0. The shared-worktree problem

All three models wrote a new test file for Prompt 7 into the *same*
`proj2/mealslot` checkout, sequentially, not in parallel isolated copies.
Checked directly this session — both files still exist on disk:

```text
tests/lib/scoring.test.ts             1592 bytes*  modified 12:58
tests/lib/scoring.codex-v2.test.ts    2117 bytes*  modified 12:59
```
*(sizes as observed; the point is both files are present and distinctly timestamped)*

Report save times: Claude 12:51 → Gemini 13:03 → Codex 13:04. Claude and
Gemini's Prompt 7 answers both target the same path,
`tests/lib/scoring.test.ts` — Gemini's report explicitly says it wrote to
that exact filename, and the file's last-modified time (12:58) falls between
Claude's report (12:51) and Gemini's (13:03), meaning **Gemini overwrote
Claude's test file with its own before running the full suite.** Codex,
running last, avoided the collision by using a distinct filename
(`scoring.codex-v2.test.ts`) — and says so explicitly in its own Weaknesses
section: *"The full-suite count includes pre-existing untracked tests in the
shared worktree, so it describes this exact workspace state rather than a
clean checkout."* Codex is the only one of the three that self-flagged this.

**Practical effect:** the three "live execution" headline numbers for
Prompt 8 are not directly comparable as three runs of the same repo state:

| Model | Files collected | Tests | Pass | Fail | Skip | Collection errors noted |
|---|---|---|---|---|---|---|
| Claude | 85 | 492 | 475 | 16 | 1 | 4 files, flagged as a distinct issue |
| Gemini | 87 | 498 | 482 | 15 | 1 | not mentioned |
| Codex | 86 | 495 | 479 | 15 | 1 | 4 files, flagged as a distinct issue |

Claude ran first, against the "cleanest" state (only its own added test
file present). Gemini's numbers reflect a state with an extra/overwritten
test file Claude had already added. Codex's reflect a state with *two* extra
scoring-test files (Gemini's leftover plus Codex's own). None of these three
numbers should be read as "the" ground-truth test count for this repo —
they're each accurate for the moment they were captured, in a worktree that
kept changing underneath them.

**What survives this contamination intact:** the *substantive* defect
catalog. All three independently reproduced the same 8 seeded regression
bugs (`uc-regression-bugs.test.ts`, BUG-01 through BUG-08) and substantially
the same ~7 additional real, deterministic failures (favorites text-locator
ambiguity, stale places-URL assertion, `updateUserDetails` stale-refetch,
party join/state code-validation gaps) with matching root causes. The
headline counts drifted; the actual bugs found did not. That's a real point
in favor of all three as investigators, independent of the worktree noise.

---

## 1. Summary table

| # | Prompt | Claude | Gemini | Codex | Notes |
|---|---|---|---|---|---|
| 1 | First contact | Earned Keep | Earned Keep | Earned Keep | All three independently caught the README's Next 15/16, SQLite/Postgres, and "future login" contradictions. |
| 2 | Module → user goals | Earned Keep | Earned Keep | Earned Keep | All three: one goal, no dead code, correct 429/`RATE_LIMIT` citation. |
| 3 | Use case + edges | Earned Keep | Earned Keep | Earned Keep | Converged on the same 3 handled / distinct unhandled extensions for UC7. |
| 4 | Undocumented product | Earned Keep | Earned Keep | Earned Keep | All three: existing account/auth system contradicting the README's roadmap is the top finding. |
| 5 | Fragile areas | Earned Keep | Earned Keep | Earned Keep | Same top-3 files (`page.tsx`, `PartyClient.tsx`, `SlotMachine.tsx`/spin route), same churn numbers. |
| 6 | Broken build | Earned Keep | Earned Keep | Earned Keep | **Diverges sharply on outcome** — see §2.1. |
| 7 | Naked-code tests | Earned Keep | Earned Keep | Earned Keep | All three wrote and ran real, passing tests against `weightedSpin`. |
| 8 | Traceability | Earned Keep | Earned Keep | Earned Keep | Numbers diverge (worktree contamination, §0); substance converges. Claude and Codex both independently caught 4 silently-dropped test files; Gemini didn't mention it. |
| 9 | Then vs now | Earned Keep | Earned Keep | **Abandoned** | Real three-way split on instruction interpretation — see §2.2. |
| 10 | Honest rewrite | Earned Keep | Earned Keep | Earned Keep | Claude and Codex both explicitly marked coverage claims UNCOVERED given the prompt supplies test filenames but no bodies; Gemini rewrote without flagging that limitation. |
| 11 | Dependency map | Earned Keep | Earned Keep | **Abandoned** | Codex declined to cite code read-sites the prompt doesn't supply; Claude/Gemini did anyway — see §2.3. |
| 12 | Public surface | Earned Keep | Earned Keep | Earned Keep | Route/method counts: Gemini 19/17 (correct), Codex 19/18 (correct), **Claude says "18 routes" (undercount — should be 19)**. |
| 13 | Naming/pattern drift | Earned Keep | Earned Keep | Earned Keep | Same core drifts (auth-id naming, error envelopes, Zod vs. manual validation) found by all three, independently cited. |
| 14 | Data model | Earned Keep | Earned Keep | Earned Keep | All three: `savedMeals` vs. `Favorite` duplication, `Party.hostId` missing relation. |
| 15 | Onboarding | Earned Keep | Earned Keep | Earned Keep | All three: SQLite/Postgres contradiction is the real blocker; Claude additionally found (via live execution) that the blocker goes deeper — see §2.1. |

---

## 2. Notable findings

### 2.1 Prompt 6 — does the build actually succeed, and on what?

Three different outcomes, not just three different write-ups:

- **Codex**: build fails exactly as the pasted example — Turbopack can't
  fetch Bungee/Sora from Google Fonts over TLS. Classified environment/setup,
  95% confidence. Did not attempt to get past it.
- **Claude**: reproduced the identical TLS failure independently, then went
  three layers further — confirmed via `curl` that the sandbox sits behind a
  TLS-intercepting proxy (font fetch and `registry.npmjs.org` both failed
  identically, both succeeded with `-k`); found no `.env.local` existed;
  found `STACK_SECRET_SERVER_KEY` is genuinely absent from `.env.example`
  despite `@stackframe/stack` being a real dependency; found `.env.example`'s
  own placeholder value for `NEXT_PUBLIC_STACK_PROJECT_ID` fails Stack
  Auth's own UUID validation at construction time. Only after supplying a
  `.env.local` with real Stack Auth/Maps/YouTube credentials did
  `pnpm build` succeed (7.1s, 17/17 static pages, verified with actual
  build output pasted in the report).
- **Gemini**: reports `pnpm build` "completed successfully in 7.5s with
  static page generation 17/17" in "an internet-connected environment" — one
  line, no mention of `.env.local`, `STACK_SECRET_SERVER_KEY`, or how Stack
  Auth's UUID validation was satisfied.

Gemini's claim is the least-evidenced of the three and, given Claude's much
more granular chain (which independently rediscovered the exact same TLS
symptom before going further), is more likely incomplete than contradictory
— e.g. Gemini's environment may have had real credentials preconfigured that
its report simply doesn't mention. Either way, **Claude's account is the one
to trust for "what does it actually take to get `pnpm build` to succeed
here"**: not just network access, but a `.env.local` with a real, valid
Stack Auth project ID — something no other report (v1 or v2) had previously
established. That's a genuine new finding this run surfaced.

### 2.2 Prompt 9 — a three-way split caused by an ambiguous instruction, not a model error

Prompt 9 asks the model to compare the pasted legacy-style code (`lib/rng.ts`)
against "a current mainstream library or language feature" — which
structurally requires bringing in library knowledge that isn't and can't be
in the pasted material, since the pasted material only shows the *old* code.

- **Claude and Gemini** both treated general knowledge of the JS
  seeded-PRNG ecosystem as fair game (Claude names `pure-rand`; Gemini
  compares against `crypto.getRandomValues`/`seedrandom`/`pure-rand`), and
  both landed on the same substantive verdict: don't migrate, the existing
  code is fine for its actual use case.
- **Codex** read the "answer using only the content pasted inside
  prompts.md" instruction more strictly, treated naming any specific library
  as importing outside knowledge, and marked the prompt **Abandoned —
  insufficient fixed input**, offering only what could be said about the old
  code alone.

This isn't really a case of one model being wrong — it's a real ambiguity in
the instructions given to all three (mine, from the previous turn), which
said "answer from pasted content only" without carving out an exception for
prompts that are inherently a which-is-better comparison against something
that was never going to be pasted. Codex's reading is arguably the more
epistemically careful one; Claude and Gemini's is the more useful one. Worth
fixing in the instructions if this prompt set is run a third time, not worth
scoring against Codex.

### 2.3 Prompt 11 — same instruction ambiguity, opposite resolution

Prompt 11 asks for the environment variable *and* "cite where in the code
it's read." `prompts.md`'s Prompt 11 section pastes `package.json` and
`.env.example` only — no source files. Claude and Gemini both cited specific
`lib/*.ts:LINE` read-sites anyway (Gemini: `lib/neon.ts:15`,
`app/handler/[...stack]/page.tsx`; Claude explicitly *declined* to do this
for prompt 11's un-sourced variables, but did cite lines for the ones that
happen to also appear as pasted code elsewhere in the file for other
prompts). Codex marked this one **Abandoned — insufficient fixed input**
too, for the same reason as Prompt 9: the prompt asks for a citation the
paste doesn't support.

Cross-checking Gemini's specific citation here (`app/handler/[...stack]/page.tsx`)
against what's actually pasted anywhere in `prompts.md`: that file is never
pasted or even named anywhere in the file. This one looks like a real
fabrication, not a mislabeled-but-correct citation like the pattern in §3 —
Gemini asserted a source location for material it was never given.

### 2.4 Route count in Prompt 12 — Claude undercounts

`prompts.md`'s Prompt 12 list has 19 method/path rows across 17 route files
(recounted directly: `dishes` has 2 methods, `dishes/[id]` has 2 methods, the
other 15 have 1 each = 19). Gemini ("19 method/path combinations across 17
API routes") and Codex (19-row table, correctly enumerated) both match this
exactly. Claude's report says "18 routes" — a small undercount. Worth noting
for balance: Claude's report is the deepest of the three on almost every
other axis, but isn't immune to a basic counting slip.

---

## 3. Citation-format accuracy — the sharpest, most checkable divergence

For the text-only prompts (1–5, 9–15), Claude and Codex both cite
`prompts.md:LINE` explicitly — i.e., the line number *within the prompt
file itself*, which is exactly what's checkable against a document the
grader actually has open. Spot-checked three of these this session; all
three landed exactly on the claimed content:

| Claim | prompts.md line | Verified content at that line |
|---|---|---|
| Claude: 429 rate-limit response at `prompts.md:422-428` | 422–428 | `if (b.tokens <= 0) { ... return Response.json({ code: "RATE_LIMIT", ... }, { status: 429 }); }` — exact match |
| Claude: `provider = "postgresql"` at `prompts.md:1857` | 1857 | `provider = "postgresql"` — exact match |
| Gemini's equivalent citation, `lib/rateLimit.ts:423-428` | (compare to `prompts.md:423-428`) | Same content as above — correct content, **wrong file attribution** |

Gemini's report cites everything as `<source-file-path>:<line>` — e.g.
`lib/rateLimit.ts:423-428`, `prisma/schema.prisma:1857`,
`app/api/videos/route.ts:521-526`. Every one of these numbers checked this
session (three spot-checks, all confirmed) turns out to be the line number
**within `prompts.md`**, not within the named source file — `lib/rateLimit.ts`
is 57 lines long in reality; `prisma/schema.prisma` is 82 lines long;
`app/api/videos/route.ts` is 129 lines long. None of Gemini's cited line
numbers could possibly be real line numbers in those files. The content
itself is correct in every case checked — Gemini clearly did read and use
the right material — but the citation format is systematically broken
across the entire report, in a way that would send anyone trying to verify a
claim to the wrong place every time. Combined with §2.3's `app/handler/[...stack]/page.tsx`
citation (which doesn't correspond to anything pasted anywhere), Gemini's v2
report is meaningfully less trustworthy to spot-check than the other two,
despite reaching largely correct substantive conclusions throughout.

Claude and Codex, by contrast, both independently landed on the disambiguated
`prompts.md:LINE` convention without being told to — worth noting as a
genuinely good, convergent practice neither was explicitly instructed to
adopt.

---

## 4. Scorecard

| | What this run adds beyond v1 | Where this run falls short |
|---|---|---|
| **Claude** | Went furthest on Prompt 6 (traced 4 stacked failure layers to a real, previously-unknown repo gap: `STACK_SECRET_SERVER_KEY` undocumented + invalid placeholder UUID); found the silently-dropped-4-test-files bug and gave it the deepest root-cause (jsdom/parse5 + `@vitest-environment jsdom` override); explicitly separated one order-dependent failure from the 15 deterministic ones. | Undercounted routes in Prompt 12 (18 vs. 19); Prompt 9's library choice (`pure-rand`) isn't itself grounded in anything pasted. |
| **Gemini** | Reached the same substantive conclusions as Claude on almost every static prompt, efficiently. | Systematically broken citation format across the entire report (§3); one apparent fabricated citation (§2.3); least-evidenced build-success claim (§2.1); didn't catch or mention the dropped-test-files bug that both other models found. |
| **Codex** | Self-flagged the shared-worktree contamination risk — the only one of the three to do so; declined to fabricate citations for prompts 9/11 where the paste genuinely doesn't support the ask; independently corroborated Claude's dropped-test-files finding. | Its strict reading of "pasted content only" cost it real answers on Prompts 9 and 11 that Claude and Gemini both managed to give usefully (§2.2, §2.3) — arguably too conservative, not too permissive. |

**Net read:** this run is a large improvement over v1 — nearly every prompt
now shows genuine three-way agreement on substance, which is what fixing the
input was supposed to buy. The two things worth fixing before a v3 run: (1)
don't let multiple agents write to the same test file path in a shared
worktree — give each model its own branch or worktree, not just a distinct
filename; (2) clarify the "pasted content only" instruction to explicitly
allow general domain/library knowledge (Prompt 9) and explicitly forbid
citing unpasted source locations (Prompt 11) rather than leaving both
readings open, which is what produced the Claude/Gemini vs. Codex split.
