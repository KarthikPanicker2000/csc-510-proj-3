# MealSlot D3 — P1 Automation Results Snapshot

**Status:** Second automation batch  
**Command:** `node scripts\run-playwright.cjs --grep '@p1'`  
**Environment:** Chromium; Next.js on `127.0.0.1:3100`; WebSocket service on `127.0.0.1:4101`; isolated PostgreSQL database `mealslot_test`; 59 seeded dishes  
**Product behavior changes:** None  
**Summary:** 11 registered — 6 PASS, 3 FAIL, 2 BLOCKED

## Results

| Test | Why we tried it | Expected | What happened | Result | Evidence / explanation |
|---|---|---|---|---|---|
| `TC-UC16-02` | Validate nickname boundaries before party/member creation. | Empty, whitespace-only, and 25-character names are rejected. | Empty and 25-character values returned 400, but whitespace-only returned 200 and created a party. | **FAIL** | Trace retained. Route validates length without trimming whitespace. |
| `TC-UC17-02` | Reject malformed and nonexistent party codes without side effects. | Malformed codes return validation errors; absent six-character code returns not found; membership count is unchanged. | Both malformed lengths returned 400, nonexistent code returned 404, and the control party retained only its creator. | PASS | API and state assertions. |
| `TC-UC14-03` | Ensure authoritative membership survives a failed leave request. | Failed leave does not remove either valid membership. | Invalid member deletion returned 500; subsequent state still contained host and joined member. | PASS | API and state assertions. The page itself does not call the leave endpoint, so this covers the authoritative API slice. |
| `TC-UC08-01` | Prove authenticated favorite persistence and uniqueness. | Saved dish ID is stored exactly once. | `/api/user/saved` returned the expected collection and the test database stored one copy. | PASS | API plus direct isolated-DB assertion. |
| `TC-UC12-01` | Resolve an authenticated saved collection across categories. | Both stored IDs resolve once and represent two categories. | Catalog resolution returned both IDs once with two distinct categories. | PASS | API plus isolated-DB setup. This batch covers retrieval/resolution; provider-authenticated browser filtering remains separate. |
| `TC-UC13-01` | Prove one favorite can be removed durably without altering another. | Removed ID stays absent; retained ID remains. | Server response and database both contained only the retained ID. | PASS | API plus direct isolated-DB assertion. |
| `TC-UC04-03` | Force party-spin fallback and assess allergen safety. | Forced internal-spin failure returns only allergen-safe fallback dishes. | No supported live failure-injection seam exists without changing product code or replacing its internal route. | **BLOCKED** | Registered skip with reason in raw output. |
| `TC-UC03-01` | Prove keep-vote quorum across three real browser sessions. | Host spin synchronizes to both members; two keep votes lock slot 0 everywhere. | Host received dishes, but both joined sessions remained at zero dishes and the lock state never appeared. | **FAIL** | Three screenshots and trace retained. Joined clients lack the returned member ID, and the raw-WebSocket client does not match the Socket.IO server protocol. |
| `TC-UC03-03` | Ensure switching Keep to Reroll replaces one member's vote. | Keep becomes 1/0, then switching produces 0/1 for that slot. | Host browser displayed the expected vote-count transition. | PASS | Browser/component integration assertions. |
| `TC-UC20-01` | Independently verify two-way party chat delivery. | Both browsers show host message then member reply exactly once. | Each sender saw its local echo, but neither remote browser received the other message. | **FAIL** | Two screenshots and trace retained. The transport mismatch prevents cross-browser delivery. |
| `TC-UC20-03` | Verify the same-origin BroadcastChannel fallback boundary. | With no socket URL, same-origin tabs exchange chat while a separate origin/device does not. | The production E2E bundle has `NEXT_PUBLIC_WS_URL` compiled in and the client exposes no runtime transport switch. | **BLOCKED** | Registered skip with reason in raw output. |

## Defect findings

1. **Whitespace nickname accepted:** party creation checks string length but does not trim before validation.
2. **Joined browser lacks operational member identity:** the page discards `memberId` returned by `/api/party/join`, while `PartyClient` only initializes it for the creator path. This disables joined-member voting.
3. **Realtime protocol mismatch:** `lib/realtime.ts` sends raw WebSocket JSON, but `ws-server/server.js` is a Socket.IO server. Host spin broadcasts and chat messages therefore do not reach separate browser sessions.

These are observations of the cloned application. No production source was corrected.

## Suggested next batch

1. Complete party spin/locking branches: `TC-UC03-02`, `TC-UC04-01`, `TC-UC04-02`, `TC-UC04-04`, and UC05.
2. Cover guest favorites and failure reconciliation: `TC-UC08-02`–`04`, `TC-UC12-02`–`04`, and `TC-UC13-02`–`04`.
3. Cover party lifecycle branches: `TC-UC14-01`, `TC-UC14-02`, `TC-UC14-04`, `TC-UC16-03`, `TC-UC17-03`, and `TC-UC17-04`.
4. Add chat empty-input and session-only checks: `TC-UC20-02` and `TC-UC20-04`.
