# Comparing the Five Use-Case Documents

Each list was checked against the actual source in `proj2/mealslot` (route handlers, `lib/scoring.ts`, `lib/party.ts`, `lib/dishes.ts`, `PartyClient.tsx`, etc.). "Better/worse" below is relative to the other four lists, not an absolute grade.

---

## Sebastian_Use_Cases.md

**Better than the others at:** mechanism-level accuracy on the app's least obvious behaviors. It is the only document that correctly describes the 10-second deterministic-spin window, the vote/quorum reroll mechanic in `PartyClient.tsx`, the exact `mergeConstraints` conflict thresholds, and the `BroadcastChannel`-vs-WebSocket fallback for cross-device party sync. It also consistently distinguishes guest (localStorage-only) behavior from authenticated (DB-persisted) behavior, which several other lists blur together.

**Worse than the others at:** economy and skimmability. Main-success-scenario steps and extensions are both packed into single table cells as long numbered prose runs rather than being visually separated, which makes it harder to scan than Karthik's or Cameron's cleaner tabular layout. It also has the least stakeholder analysis of any list — most entries name only "Player" or "User" rather than exploring secondary stakeholders (hosts, other members, external services).

---

## Carlos_Use_Cases_Claude.md

**Better than the others at:** implementation-verifiable precision. This is the only list that caught the legacy lock-format-ignored behavior in the spin schema, the exact "retry up to 6 times, then fall back to a hardcoded menu" logic in `/api/party/spin`, and the 2-second Stack-Auth display-name polling loop. Its extensions are keyed to specific numbered steps (2a, 4a, 6a) in the Cockburn style, which makes it easy to trace exactly which part of the main flow each variation branches from.

**Worse than the others at:** staying at the "what, not how" level. Several use cases leak implementation details that belong in a design doc rather than a use case — JSON field names, specific function names (`ensureUserInDB`, `updateUserDetails`), and internal retry counts appear directly in the main success scenarios. It also has a real coverage gap: its party-spin use case (UC-17) never mentions the vote/keep/reroll mechanic that actually drives most in-party decisions, describing group spins as purely host-triggered.

---

## Carlos_Use_Cases_Qwen3_8b.md

**Better than the others at:** breadth of stakeholder identification and self-documentation. Every use case lists three to four distinct stakeholder roles (including plausible but unverifiable ones like "Data Analyst," "Nutritionist," "Restaurant Owner"), and every entry cites its source files under "Derived from," which is a nice traceability habit none of the other four lists adopted.

**Worse than the others at:** factual grounding. This is the most hallucination-prone of the five lists — for example, it claims a party-code collision causes the system to "generate a new unique party code" (UC2), when the actual `/api/party/create` route has no collision-retry logic at all and would simply fail with a generic 500 on a `@unique` constraint violation. It also inflates its count by splitting one underlying feature (`/api/dishes` and `/api/filters`) into three near-duplicate use cases ("View Dish Details," "View Dish Tags," "View Dish Filters") rather than surfacing 20 genuinely distinct behaviors. Consistent with its own header noting it was generated locally via an 8B parameter model, several extensions read as generic web-app boilerplate (mobile-responsive layouts, save-recipe buttons, ingredient checklists) with no corresponding code.

---

## Karthik_USE_CASES.md

**Better than the others at:** discipline and consolidation. Its main success scenarios are the cleanest pure happy-paths of any list — genuinely free of branch logic — with all variation pushed into extensions, exactly as the format intends. It's also the only list to synthesize an entire party round (categories → constraints → spin → voting → chat → implicit host handoff) into one coherent 20th use case instead of scattering it across several shallow ones, and its account-lifecycle coverage (create/sign-in/sign-out/manage-profile) is the most complete of any document.

**Worse than the others at:** granularity and independent verifiability. Because related behaviors are folded into fewer, broader use cases, some real edge cases (e.g., the exact vote quorum arithmetic, or the fallback-menu behavior in party spins) are only alluded to rather than pinned down with the same precision Carlos-Claude achieves. A few extensions describe outcomes ("system enforces host authority," "quorum decisions") in idealized procedural language that slightly overstates how tightly the actual code enforces those guarantees under races like disconnects during a vote.

---

## D2_Cameron_Gemini_use_cases.md

**Better than the others at:** formal structure and stated methodology. It is the only document that opens by declaring the rules it followed (clean main scenarios, "what not how" phrasing, no UI/DB talk) and it follows through with the most consistent sub-numbered extension format (`.1`, `.2`) of any list, which makes its edge cases easy to enumerate and count.

**Worse than the others at:** grounding in the real feature set — it is the most embellished of the five. It invents functionality that doesn't exist in the codebase, such as full-day plans computing "combined preparation time and nutritional totals" (UC2), a persisted spin-history browsing page (UC12), password-reset and duplicate-nickname-suffixing flows, and a user-facing "configure 1–4 dishes" control (UC18) that in reality is a hardcoded `DISH_COUNT = 3` in the solo page plus an orphaned `DishCountInput` component that no page actually renders. Like Carlos-Claude, it also omits the vote/quorum reroll mechanic entirely, presenting group spins as a single unilateral host action.

---

## Summary Table

| Document | Strongest trait | Weakest trait |
|---|---|---|
| Sebastian_Use_Cases.md | Most accurate on subtle/non-obvious mechanics | Dense prose, thin stakeholder analysis |
| Carlos_Use_Cases_Claude.md | Most implementation-verifiable precision | Leaks "how" into "what"; misses party voting |
| Carlos_Use_Cases_Qwen3_8b.md | Broadest stakeholder lists, cites sources | Most hallucinated/generic content |
| Karthik_USE_CASES.md | Cleanest happy-paths, best consolidation | Coarser granularity, some idealized language |
| D2_Cameron_Gemini_use_cases.md | Clearest stated methodology and formatting | Most invented/unimplemented features |
