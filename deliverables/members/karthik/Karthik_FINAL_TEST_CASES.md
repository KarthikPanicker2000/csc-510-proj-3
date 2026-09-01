# MealSlot Final Test Case Specification

**Use-case baseline:** `FINAL_TOP_20_USE_CASES_SEBASTIAN_PRESERVED.md`  
**Assignment:** CSC 510 Project 1a — Testing  
**System under test:** MealSlot repository as cloned  
**Prepared by:** Software Test Engineering  
**Document status:** Test design complete; all execution results are currently NOT RUN  

## 1. Assignment alignment

This specification designs tests for the final 20 use cases. It is an input to, not a substitute for, the graded D3 and D4 evidence.

- **D3:** executable test code link, samples of raw test output, and a results table containing test, why it was tried, expected behavior, and what happened. Genuine failures remain in the report and are explained.
- **D4:** one-row-per-test traceability between tests and use cases, plus an evidence-based assessment of the repository's original tests and their blind spots.
- Project 1a is **report, do not repair**. Product bugs, code rot, and specification mismatches are findings; the team must not change product behavior to force tests to pass.
- The final report must use ACM `acmart` two-column LaTeX. The 2–5 minute video must show the software running, real test execution, one pass, one genuine failure, and one use case end to end.

## 2. Suite strategy and result rules

The suite contains **80 uniquely identified test cases: four per final use case**. Main journeys are exercised through the browser. Validation, deterministic selection, failures, and boundaries use the lowest layer that can prove the behavior without excessive mocking.

| Result | Meaning |
|---|---|
| PASS | Every observable expected result matched. |
| FAIL | At least one expected result differed from the cloned product. Preserve evidence; do not repair it in Project 1a. |
| BLOCKED | A named prerequisite or external service prevented execution after documented setup attempts. |
| NOT RUN | The case has not been attempted. This is the initial state of every case here. |

| Label | Meaning |
|---|---|
| P0 | Central journey, safety, security, authorization, or data-integrity risk; automate first. |
| P1 | Important feature, boundary, or resilience behavior. |
| P2 | Lower-risk compatibility/presentation behavior. |
| E2E | Playwright browser test, with isolated contexts where needed. |
| API | Playwright request/HTTP test against the running backend. |
| Integration | Vitest with real modules and an isolated database where appropriate. |
| Unit/component | Vitest or Testing Library with narrowly controlled dependencies. |

## 3. Controlled environment and fixtures

| Item | Baseline |
|---|---|
| Commit | Record exact fork URL and commit SHA for every run. |
| Application | Build and run the unchanged frontend/backend locally. |
| Database | Dedicated PostgreSQL test database with repository schema and deterministic seed. |
| Browser | Chromium for all E2E tests; repeat selected P0 flows in a second engine if practical. |
| Authentication | Disposable Stack Auth identities; never record real passwords, keys, or personal data. |
| Realtime | Separate Playwright browser contexts for members; WebSocket and BroadcastChannel modes tested separately. |
| External APIs | Deterministic request interception for routine tests; optional separately tagged live-provider smoke checks. |
| Evidence | Raw console output, HTML report, failure trace, relevant screenshot/video, request/response, and DB evidence without secrets. |

| Fixture | Purpose |
|---|---|
| `Guest-A` | Signed-out context with clean storage. |
| `User-A` | Account with no saved meals/allergens. |
| `User-B` | Account with known saved meals and allergens. |
| `Auth-Only` | Valid provider identity with no MealSlot profile. |
| `Host-A` | Party creator in isolated context A. |
| `Member-B`, `Member-C` | Party participants in isolated contexts B and C. |
| `SafeDish` | Seeded dish with known category, tags, allergens, price, health, and time attributes. |
| `BlockedDish` | Seeded dish containing the allergen selected by a test. |
| `EmptyCategory` | Controlled category/filter combination with no eligible dish. |

## 4. Test cases

### UC01 — Spin for a Meal

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC01-01 | Prove the primary solo spin journey. | Guest-A; three valid categories; cooldown zero; seeded catalog. | Select categories, optional filter/power-up, click Spin, capture `/api/spin` request and displayed reels. | One request contains the selected configuration; three results display; each eligible result respects its category/filter; cooldown starts. | E2E + API | P0 |
| TC-UC01-02 | Cover missing category and zero-candidate extensions 4a/4b. | Variant A omits a category; variant B uses `EmptyCategory`. | Submit each variant. | A is rejected with category-required behavior and no valid spin result. B completes with `No options` only in the affected slot. | API | P0 |
| TC-UC01-03 | Verify lock validity and deterministic repeat extensions 5a/5b. | Existing result; one valid lock and one lock made incompatible; fixed time within 10-second seed window. | Re-spin identical input twice, then change filters so a lock is invalid. | Identical seed/input returns the implementation's repeat result; valid lock remains; incompatible lock is dropped and replaced. | API/integration | P1 |
| TC-UC01-04 | Verify server-error fallback and client cooldown extensions 6a/7a. | Intercept first spin with 500; then allow a successful spin. | Spin during failure; retry successfully; immediately click Spin repeatedly. | Failure behavior is visible without crash; successful spin renders; during cooldown the control prevents an additional request. | E2E | P0 |

### UC02 — Set Party Dietary Preferences and Resolve Conflicts

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC02-01 | Prove multi-member preference merge. | Host-A, Member-B, Member-C in one active party. | Give members differing diets, allergens, budget, and time bands; save each; fetch party state. | Preferences persist per member; merged diet follows implemented strictness; allergens are unioned; minimum budget/time bands are returned and shown to clients. | E2E + API | P0 |
| TC-UC02-02 | Prove merged constraints affect a later party spin. | Party from TC-UC02-01; catalog contains allowed and blocked dishes. | Host spins and inspect all returned dishes. | No returned eligible dish violates merged allergens/diet; all clients receive the same selection. | E2E | P0 |
| TC-UC02-03 | Preserve authoritative state when update fails (3a). | Existing merged constraints; intercept update with 500. | Member changes preferences and submits; reload party state. | Error is visible; prior member preferences and merged constraints remain authoritative; peers do not receive a false committed update. | E2E + API | P0 |
| TC-UC02-04 | Detect both documented conflict rules (4a/4b). | Controlled preference sets. | Create mutually incompatible diets; separately combine vegan with at least three blocked allergens. | Structured conflict is returned for each rule with the documented resolution suggestion; no unsafe result is silently accepted. | Unit + API | P1 |

### UC03 — Vote on a Spin Result

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC03-01 | Prove keep-majority locking. | Three connected members and a completed party spin. | Host-A and Member-B vote Keep on slot 0. | Votes are recorded once per member; majority is calculated from connected members; slot 0 locks and the state reaches all clients. | Multi-context E2E | P0 |
| TC-UC03-02 | Prove reroll-majority behavior. | Same party; unlocked slot 1. | Two members vote Reroll on slot 1. | Only slot 1 is rerolled by the authorized flow; other slots stay unchanged; new state is broadcast. | Multi-context E2E | P0 |
| TC-UC03-03 | Ensure changing a vote replaces rather than duplicates it (2a). | Three members; no quorum yet. | Member-B votes Keep, then changes to Reroll before another vote. | Member-B contributes exactly one current vote; old vote is removed; displayed counts and quorum use the replacement. | Component/integration | P0 |
| TC-UC03-04 | Verify disconnect changes live quorum (4a). | Three members; one vote short of old threshold; heartbeat controllable. | Disconnect Member-C and advance beyond presence timeout. | Timed-out member leaves connected count; quorum recalculates and resulting lock/reroll state matches the new threshold. | Integration + E2E | P1 |

### UC04 — Spin the Party Slot Machine

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC04-01 | Prove host party spin, uniqueness, and synchronization. | Active party; known merged constraints; three categories. | Host spins; inspect `/api/party/spin`, database/state, and two clients. | Three distinct eligible dishes are returned and displayed identically to all active clients. | Multi-context E2E | P0 |
| TC-UC04-02 | Cover default category and lock branches 2a/3a. | Existing selection with one locked slot. | Call party spin without categories; then with a valid lock. | Missing categories use dinner default; locked dish remains at its index; only unlocked slots change. | API | P1 |
| TC-UC04-03 | Determine whether internal-spin fallback is actually allergen-safe (4a). | Merged constraints block allergens present in the hardcoded fallback; force internal `/api/spin` failure. | Request party spin and inspect each fallback result. | Per use-case promise, no returned dish contains a merged blocked allergen. Any violating fallback is recorded as a genuine safety FAIL, not repaired. | API | P0 |
| TC-UC04-04 | Verify six-attempt exhaustion produces placeholders (5a). | Stub internal spins to return duplicates/no candidates. | Request party spin and count attempts/results. | Attempts are bounded; filled slots remain unique; unresolved slot is `No options`; request terminates without hanging. | API | P0 |

### UC05 — Lock a Reel and Re-Spin

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC05-01 | Prove normal lock-and-respin. | Solo result with three populated slots. | Lock slot 0 and spin after cooldown. | Slot 0 retains the same dish ID; unlocked slots are selected afresh and deduplicated against the lock. | E2E | P0 |
| TC-UC05-02 | Cover multiple locks and unlock transition. | Existing result. | Lock slots 0/1; spin; unlock 1; spin again. | Both locks persist in first spin; only slot 0 must persist in second; lock icons and request payload match. | E2E | P1 |
| TC-UC05-03 | Verify legacy index-only lock payload is ignored (3a). | Direct API access and known prior IDs. | Send locked array containing only indices. | Request is handled without crash; index-only entries do not preserve prior dishes and are treated as unlocked. | API | P1 |
| TC-UC05-04 | Cover no-alternative and incomplete deduplication branches 5a/6a. | Catalog fixtures with one candidate and duplicate candidates. | Re-spin unlocked slots against constrained fixtures. | No-candidate slot becomes placeholder; response remains bounded; actual behavior for fewer than three unique dishes is captured exactly. | API/integration | P0 |

### UC06 — Update Display Name

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC06-01 | Prove provider-to-database-to-header synchronization. | User-A on Account page. | Change Stack Auth display name; wait just over one poll interval; query DB and header. | One update writes the new name; context refresh occurs; header displays the new value. | E2E + DB | P1 |
| TC-UC06-02 | Ensure unchanged names do not cause repeated writes (2a). | Stable display name; update endpoint observable. | Remain on page for at least three poll cycles. | No update request/write occurs solely because polling ran. | E2E | P1 |
| TC-UC06-03 | Skip null/empty provider name (3a). | Stub auth provider with no display name. | Run poll cycle. | Database name is unchanged and no malformed update is sent. | Component | P1 |
| TC-UC06-04 | Document behavior when DB update fails (4a). | Existing old name; force first DB update failure, later restore. | Change name, observe header/log, then allow another poll. | Error is captured; no false durable DB claim is made; later successful synchronization produces provider name consistently. | Component + E2E | P1 |

### UC07 — View Recipe Videos for a Dish

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC07-01 | Prove normal grouped video lookup. | Three displayed dishes; deterministic successful YouTube stub. | Click Cook at Home and inspect request/cards. | Modal opens; each dish is queried as `<dish> recipe`; at most two normalized video cards appear per dish with usable URL/thumbnail. | E2E + API | P1 |
| TC-UC07-02 | Verify no-key deterministic fallback (4a). | `YOUTUBE_API_KEY` absent in isolated test environment. | Make identical `/api/videos` requests twice and open modal. | Stub notice/content is returned; identical input gives deterministic content; no key or stack trace leaks. | API + E2E | P1 |
| TC-UC07-03 | Preserve partial success when one dish lookup fails (4b). | Stub one YouTube request as HTTP error and others success. | Open videos for three dishes. | Failed dish has empty list and error metadata; successful dishes retain cards; modal remains usable. | API | P1 |
| TC-UC07-04 | Render a legitimate empty group (6a). | Stub zero results for one dish. | Open modal. | Affected dish shows no cards/accurate empty state; other groups remain; no invented video appears. | Component/E2E | P2 |

### UC08 — Save a Meal to Favorites

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC08-01 | Prove authenticated persistence. | User-A; unsaved displayed `SafeDish`. | Click heart; reload; open Favorites; inspect DB/profile. | Heart becomes saved; dish ID persists exactly once; Favorites displays the dish after reload. | E2E + DB | P0 |
| TC-UC08-02 | Prove guest session storage. | Guest-A; clean local storage. | Save dish; navigate to Favorites and reload same browser context. | Save is stored only in browser storage and is visible for that guest context; no authenticated profile write occurs. | E2E | P1 |
| TC-UC08-03 | Verify failure rollback promise (3a). | User-A; intercept persistence update with 500. | Click heart and observe immediate/final UI and profile. | Per supplied use case, error is shown and heart returns to unsaved; server state stays unchanged. A retained optimistic heart is a FAIL to document. | E2E | P0 |
| TC-UC08-04 | Verify guest-to-account non-migration (4a). | Guest-A has local favorite; disposable user can sign in. | Sign in, load profile/Favorites, compare storage and DB. | Guest favorite is not silently written into the account; actual disappearance/continued local visibility is recorded without modifying behavior. | E2E + DB | P1 |

### UC09 — Filter Meals by Allergen

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC09-01 | Safety: excluded allergen never appears. | Catalog includes `BlockedDish`; select its allergen; use several categories/seeds. | Run a parameterized set of spins and inspect result allergen arrays. | Zero returned eligible dishes contain the excluded allergen, case-insensitively; placeholder is allowed where no safe candidate exists. | API | P0 |
| TC-UC09-02 | Verify dynamic list plus static fallback (2a). | Variant A DB catalog available; variant B catalog/filter DB call fails. | Open filter menu in both variants. | A shows normalized deduplicated options from catalog/defaults. B shows documented static fallback rather than crashing. | API + E2E | P0 |
| TC-UC09-03 | Verify all candidates excluded branch (4a). | `EmptyCategory` created through selected allergens. | Spin. | Only affected slot displays `No options`; blocked dish is never substituted. | E2E + API | P0 |
| TC-UC09-04 | Verify saved-account preselection (5a). | User-B has known saved allergens, including case variants if supported. | Sign in and open filters. | Valid saved allergens are selected once; invalid/stale values are not presented as valid; later spin uses active exclusions. | E2E | P0 |

### UC10 — Register an Account

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC10-01 | Prove new identity creates linked application user. | Disposable email absent from auth provider and DB. | Complete Stack Auth sign-up; follow callback; query DB and home session. | Auth session exists; one `User` row has matching `auth_id`, display name, empty allergens/saved meals; home is personalized. | E2E + DB | P0 |
| TC-UC10-02 | Verify missing `auth_id` guard (4a). | Direct controlled call with null/missing identity. | Invoke user-creation path. | No row is created; null/error behavior matches implementation; diagnostic contains no secrets. | Unit/API | P0 |
| TC-UC10-03 | Verify idempotent returning-user upsert (5a). | Existing application user with known UUID and saved data. | Trigger ensure/create path twice with same `auth_id`. | Exactly one row remains; original UUID and saved data remain; existing user is returned. | Integration + DB | P0 |
| TC-UC10-04 | Preserve auth/DB consistency evidence on DB failure (5b). | Force application DB write failure after provider signup. | Complete signup/callback. | Application does not claim a complete linked profile; error state is visible; partial provider identity versus missing DB row is explicitly captured. | E2E + DB | P0 |

### UC11 — Apply Power-Ups to Bias Selection

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC11-01 | Prove each Power-Up changes the intended scoring input without turning a preference into a safety guarantee. | Seeded candidates include known healthy/unhealthy, cheap/expensive, and fast/slow dishes; deterministic random source. | Parameterize Healthy, Cheap, and no-more-than-30-minutes individually; calculate candidate scores and execute controlled spins. | Matching candidates receive the implemented weight advantage for the selected Power-Up; eligible nonmatching candidates are not incorrectly labelled as matches. | Unit + API | P1 |
| TC-UC11-02 | Verify combined Power-Ups are applied together. | Candidate set contains dishes matching zero, one, two, and all three priorities. | Activate two Power-Ups, then all three; inspect scores and deterministic selections. | Each active priority contributes according to the implemented scoring rule; combined scoring is deterministic under a fixed seed; no inactive priority contributes. | Unit | P1 |
| TC-UC11-03 | Verify activation, deactivation, and request state. | Solo page loaded; request capture enabled. | Toggle Healthy on; spin; toggle it off; spin after cooldown. | First request contains Healthy and UI shows it active; second request omits/deactivates it and UI returns to neutral; prior state does not leak. | E2E | P1 |
| TC-UC11-04 | Cover the no-matching-candidate extension. | Every eligible dish fails the active Power-Up but remains category/allergen eligible. | Activate the unmatched Power-Up and spin with a deterministic seed. | Spin completes from the eligible pool rather than returning an error or unsafe fallback; result is not falsely claimed to satisfy the priority. | API + E2E | P1 |

### UC12 — Browse Saved Meals

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC12-01 | Prove authenticated retrieval, catalog resolution, and category filtering. | User-B has saved dishes from at least two categories; catalog is available. | Open Favorites; record displayed IDs; choose each represented category and then clear the filter. | All resolvable saved dishes initially display once; each filter shows only its category; clearing restores the complete resolved collection. | E2E + DB | P0 |
| TC-UC12-02 | Verify account data is protected from a signed-out visitor. | Guest-A with clean storage. | Navigate directly to the Favorites URL and inspect network/UI. | No authenticated collection or prior user's dish data is exposed; sign-in requirement is displayed. | E2E | P0 |
| TC-UC12-03 | Cover stale identifier and catalog-loading failures. | Variant A: profile has SafeDish plus a syntactically valid missing ID. Variant B: intercept catalog request with failure. | Open Favorites in each variant. | A displays SafeDish and omits only the unresolved entry without crashing. B reports inability to resolve saved details and does not present stale data as current. | E2E + API | P1 |
| TC-UC12-04 | Distinguish globally empty and category-empty states. | Variant A: User-A has no favorites. Variant B: favorites exist, but none in selected category. | Open Favorites; apply the unmatched category in variant B. | A shows the global empty state. B shows an empty filtered result while preserving the underlying saved collection when filter is cleared. | E2E | P1 |

### UC13 — Remove a Saved Meal

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC13-01 | Prove successful removal is durable and isolated. | Authenticated user has at least two saved dishes. | Remove one target; wait for persistence/profile refresh; reload Favorites and query profile. | Target disappears and remains absent after reload; other saved IDs remain unchanged; no duplicate or unrelated deletion occurs. | E2E + DB | P0 |
| TC-UC13-02 | Verify removal of the final favorite. | Authenticated user has exactly one saved dish. | Remove the dish. | Collection becomes empty persistently; empty-state message replaces the card; no stale category result remains. | E2E + DB | P1 |
| TC-UC13-03 | Preserve authoritative data when removal persistence fails. | Existing collection; intercept save/update request with 500. | Remove target and allow the subsequent profile reconciliation. | Error is recorded or shown as implemented; server collection remains unchanged; target reappears after authoritative refresh rather than being falsely claimed as durably removed. | E2E | P0 |
| TC-UC13-04 | Cover refresh failure and concurrent server state. | Variant A: write succeeds but profile refresh fails. Variant B: server returns a concurrently changed collection. | Remove target and observe local state; restore service and refresh. | A may remain optimistic temporarily, but later reload confirms successful write. B reconciles to the authoritative server list without corrupting unrelated favorites. | Integration + E2E | P1 |

### UC14 — Leave a Party

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC14-01 | Prove ordinary member departure. | Host-A and Member-B in active party. | Member-B clicks Leave; inspect both clients and DB/state. | Membership/presence is removed; departure reaches host; Member-B local party state clears and landing screen appears. | Multi-context E2E + DB | P0 |
| TC-UC14-02 | Determine actual host departure behavior (2a). | Host-A plus two live members. | Host leaves; wait for presence update; attempt an authorized host action from next live member. | Stored room remains active; actual implicit-host selection and ability to continue are captured against the use-case promise. | Multi-context E2E | P0 |
| TC-UC14-03 | Preserve membership when leave fails (2b). | Intercept leave endpoint with 500. | Member clicks Leave; reload party. | Error is visible; member is still authoritative in server state and may retry; UI does not permanently claim departure. | E2E + API | P0 |
| TC-UC14-04 | Make repeat leave idempotence observable. | Member has already left. | Repeat the same leave request and inspect party. | No unrelated membership is removed and no party corruption occurs; response status/message is recorded as current behavior. | API | P1 |

### UC15 — Find Nearby Restaurants After Spinning

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC15-01 | Prove location-based venue search and normalization. | Displayed dishes; geolocation granted; deterministic Google stubs. | Click Eat Outside; supply coordinates; inspect request/cards/map. | Cuisine names and coordinates are sent; cards show normalized name/address/rating/price/distance/Maps URL; valid coordinates produce pins. | E2E + API | P1 |
| TC-UC15-02 | Cover denied and unsupported geolocation 2a/2b. | Two browser contexts: deny permission; remove geolocation API. | Start Eat Outside in each. | Both continue without coordinates using the documented location hint path; no repeated coercive prompt or false GPS claim. | E2E | P1 |
| TC-UC15-03 | Cover fallback geocode success/failure 3a/3b. | No coordinates; stub Denver geocode success, then failure. | Call places API and render results. | Success uses geocoded origin and distances; failure still returns venue text data with omitted distances and an accurate notice. | API + component | P1 |
| TC-UC15-04 | Preserve partial cuisine success (4a). | Three cuisines; one provider request errors. | Search. | Failed cuisine has empty/error entry; other cuisine venues remain; aggregate response and UI do not discard partial success. | API | P1 |

### UC16 — Create Party

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC16-01 | Prove party creation and host initialization. | Party landing page; valid nickname. | Create party; inspect code, member record, preferences, and presence. | Active unique six-character party exists; creator is first member/host; preferences initialize; code and collaborative UI display. | E2E + DB | P0 |
| TC-UC16-02 | Validate nickname 1a. | Empty, whitespace-only, and 25-character nickname variants. | Attempt creation for each. | Invalid values are prevented/rejected; no party/member record is created; exact boundary behavior is recorded. | E2E + API | P0 |
| TC-UC16-03 | Verify collision and atomic storage failure 2a/2b. | Stub code generation collision; separately fail DB transaction. | Create party in each variant. | Collision retries or fails without overwrite; storage failure returns error with no orphan party/member. | Integration + API | P0 |
| TC-UC16-04 | Verify account-allergen initialization and transport fallback 4a/6a. | User-B with saved allergens; WebSocket URL absent. | Create party; inspect host prefs; open same-origin second tab and separate-device client. | Valid account allergens initialize party preferences; BroadcastChannel supports same-origin updates only; cross-device limitation is documented. | E2E + DB | P1 |

### UC17 — Join Party

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC17-01 | Prove authenticated join. | Active code; User-A/Member-B in isolated context. | Enter code and nickname; join; inspect response, DB, both member lists. | One member row links correct party/user, returns party/member/code IDs, and displays nickname plus `you`; host sees member. | Multi-context E2E + DB | P0 |
| TC-UC17-02 | Reject invalid/nonexistent code 2a. | Malformed lengths and well-formed nonexistent code. | Submit each. | No membership/presence is created; clear validation/not-found error appears. | E2E + API | P0 |
| TC-UC17-03 | Determine duplicate-membership behavior 4a. | User-A already belongs to a party. | Submit same code again, then a different active code. | Per supplied use case, duplicate association is rejected and no second membership is created. Any allowed duplicate is recorded as mismatch. | API + DB | P0 |
| TC-UC17-04 | Cover optional nickname/default preferences and auth precondition discrepancy 5a/6a. | Variants: with nickname; without preferences; without `auth_id`. | Join for each variant. | Nickname is stored when supplied; missing preferences become defaults. Guest/no-auth behavior is recorded because route evidence suggests `auth_id` may be optional despite the supplied precondition. | API | P1 |

### UC18 — Sign In to an Account

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC18-01 | Prove returning-user authentication and profile restoration. | Registered User-B is signed out and has known saved meals/allergens. | Sign in with the configured method; follow redirect; inspect session, home filters, Favorites, and profile query. | Valid session is established; only User-B's profile is loaded; known preferences/favorites are restored; authenticated UI is displayed. | E2E + DB | P0 |
| TC-UC18-02 | Reject invalid credentials without creating state. | Disposable invalid credentials; clean browser context. | Submit invalid credentials and inspect session/application database. | Provider reports authentication failure; no authenticated session or new application profile exists; visitor may retry. | E2E | P0 |
| TC-UC18-03 | Verify valid identity with missing application profile is initialized once. | Auth-Only identity exists at provider but has no MealSlot User row. | Sign in twice, querying DB after each completion. | First completion creates one linked profile with empty saved meals/allergens; second reuses it; no duplicate User rows appear. | E2E + DB | P0 |
| TC-UC18-04 | Prevent stale/cross-user data when provider or profile loading fails. | User-A previously used browser; then sign out. Variant A: provider unavailable. Variant B: User-B authenticates but profile fetch fails. | Attempt each sign-in and inspect visible/local/network state. | Failure is accurately reported; User-A's cached personal data is not shown as User-B's; application does not claim a fully loaded authenticated profile without evidence. | E2E | P0 |

### UC19 — Sign Out of an Account

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC19-01 | Prove successful sign-out ends access. | User-B signed in on a protected/account page. | Sign out; revisit Account and Favorites directly; inspect provider session. | Session is ended; signed-out home state appears; protected pages require authentication and expose no User-B data. | E2E | P0 |
| TC-UC19-02 | Verify client caches do not leak data to the next user. | User-A has distinctive favorites/allergens and is signed in. | Sign out; sign in as User-B in the same context; inspect filters, Favorites, header, and local storage. | User-A profile/cache is cleared or replaced; only User-B data and identity are visible; no cross-account merge occurs. | E2E | P0 |
| TC-UC19-03 | Document provider sign-out failure honestly. | User-A signed in; force sign-out provider/network failure. | Request sign-out and then access an authenticated page. | Application reports failure and does not falsely claim session termination; actual remaining provider session and data exposure are captured as observed. | E2E | P0 |
| TC-UC19-04 | Verify sign-out behavior across tabs and restricted storage. | Same account open in two tabs; separate variant blocks localStorage access. | Sign out in one tab; refresh/act in the other; repeat restricted-storage variant. | Ended provider session prevents protected access after refresh; removable in-memory state clears; storage errors do not expose previous account data or crash the app. | Multi-page E2E | P1 |

### UC20 — Chat with Party Members

| ID | Why / objective | Preconditions | Procedure | Expected result | Layer | Priority |
|---|---|---|---|---|---|---|
| TC-UC20-01 | Independently trace normal party chat. | Two connected same-room members. | Host sends one message; member replies. | Both clients show both messages once, in order, with correct nicknames. | Multi-context E2E | P1 |
| TC-UC20-02 | Verify empty message does nothing (2a). | Chat open. | Submit empty and whitespace-only values by keyboard and Send button. | No broadcast or history entry occurs; UI remains usable. | Component/E2E | P1 |
| TC-UC20-03 | Prove same-origin fallback boundary (3a). | No dedicated realtime URL; two same-origin tabs and one separate-device/browser-origin client. | Send distinct messages from each environment. | Same-origin tabs exchange messages through BroadcastChannel; other device does not receive them; UI does not imply cross-device delivery. | E2E | P1 |
| TC-UC20-04 | Verify chat is session-only, not persisted. | Existing messages in active party. | Reload all clients and query party state/database for chat records. | Prior chat is absent after session/reload as implemented; no chat persistence row/API is found; meal/party state is otherwise unaffected. | E2E + DB | P1 |

## 5. Traceability summary

| Use case | Direct tests | Primary coverage |
|---|---|---|
| UC01 Spin for a Meal | TC-UC01-01–04 | Main spin; validation/no options; locks/seed; failure/cooldown |
| UC02 Party Dietary Preferences | TC-UC02-01–04 | Merge; applied constraints; failure; conflicts |
| UC03 Vote on Spin Result | TC-UC03-01–04 | Keep; reroll; vote replacement; disconnect quorum |
| UC04 Party Slot Machine | TC-UC04-01–04 | Sync/uniqueness; defaults/locks; fallback safety; bounded exhaustion |
| UC05 Lock and Re-Spin | TC-UC05-01–04 | Lock; transitions; legacy payload; scarcity/deduplication |
| UC06 Update Display Name | TC-UC06-01–04 | Sync; no-op polling; missing name; persistence failure |
| UC07 Recipe Videos | TC-UC07-01–04 | Normal results; no-key fallback; partial error; empty group |
| UC08 Save Favorite | TC-UC08-01–04 | Account persistence; guest storage; failure rollback; no migration |
| UC09 Allergen Filter | TC-UC09-01–04 | Safety; filter fallback; no options; saved preselection |
| UC10 Register Account | TC-UC10-01–04 | New identity; missing auth ID; idempotence; DB failure |
| UC11 Apply Power-Ups | TC-UC11-01–04 | Individual priorities; combinations; toggle state; no matching dish |
| UC12 Browse Saved Meals | TC-UC12-01–04 | Retrieval/filter; authorization; stale/catalog failure; empty states |
| UC13 Remove Saved Meal | TC-UC13-01–04 | Durable removal; final item; write failure; refresh/concurrency |
| UC14 Leave Party | TC-UC14-01–04 | Member leave; host leave; failure; repeated leave |
| UC15 Nearby Restaurants | TC-UC15-01–04 | GPS; denial; geocode fallback; partial provider failure |
| UC16 Create Party | TC-UC16-01–04 | Creation; validation; collision/atomicity; profile/realtime initialization |
| UC17 Join Party | TC-UC17-01–04 | Join; invalid code; duplicate membership; defaults/auth discrepancy |
| UC18 Sign In | TC-UC18-01–04 | Restore profile; invalid credentials; missing profile; failure/data isolation |
| UC19 Sign Out | TC-UC19-01–04 | End access; clear caches; provider failure; tabs/restricted storage |
| UC20 Party Chat | TC-UC20-01–04 | Delivery; empty input; fallback transport; non-persistence |

All 20 use cases have four direct tests and no test is orphaned.

## 6. D3 execution-results table

Create one row per executed test variant. The design above supplies the first three columns; execution supplies the last three.

| Test | Why we tried it | Expected | What happened | Result | Evidence / explanation |
|---|---|---|---|---|---|
| `TC-UCxx-xx` | Main step or extension being tested | Observable expected behavior | Exact observed behavior | PASS / FAIL / BLOCKED | Raw-output line, trace/screenshot, defect or cause classification |

For every run, record the command, commit SHA, environment, raw output, and relevant evidence. Classify non-passes as product defect, code rot, environment/setup, external dependency, or use-case/specification mismatch. Re-run an unexpected failure once to rule out transient setup issues, but never hide or repair a reproducible product failure.

## 7. D4 original-test assessment

D4 must map both this suite and the tests already in the cloned repository. For every original test, capture its exact name, file, mapped use case(s), behavior it proves, and important behavior it mocks or cannot prove. Report both directions:

- final use cases or extensions with no meaningful original-test coverage;
- original tests that map to no user-facing use case;
- component/API tests that pass but do not establish the end-to-end journey;
- authentication, persistence, multi-client realtime, external-provider, and safety blind spots;
- differences between original white-box tests and new black-box findings.

## 8. Recommended automation order

1. Implement deterministic P0 API/integration tests for allergen safety, spin validation, party endpoints, authentication linkage, and persistent favorites.
2. Implement P0 Playwright journeys for solo spin, save/browse/remove favorites, register/sign in/sign out, create/join/leave party, voting, and party chat.
3. Add multi-context realtime tests and explicit WebSocket/BroadcastChannel configurations.
4. Add P1 provider-fallback and failure tests using route interception; keep live-provider checks separately tagged.
5. Execute against a resettable test database and export raw output plus the results table.
6. Audit the repository's original tests and complete the D4 bidirectional traceability/coverage verdict.



