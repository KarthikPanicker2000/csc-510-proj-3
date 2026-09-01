# Top 20 Use Cases (Selected Across All Five Documents)

Selection criteria: fidelity to the actual `proj2/mealslot` implementation (verified against source — `lib/scoring.ts`, `lib/party.ts`, `lib/dishes.ts`, the `app/api/*` route handlers, and `PartyClient.tsx`), coverage of a distinct and important user goal, and quality/precision of the extensions (edge cases that really happen in the code, not generic boilerplate). Where multiple files covered the same underlying feature, the single best-written and most accurate instance was chosen.

---

### 1. Spin for a Meal — *Sebastian_Use_Cases.md*, UC1
Chosen because it is the only version that correctly captures the spin engine's actual "determinism" behavior — identical filters/locks within the same 10-second window reproduce the same result — which is a real, easily-missed property of `makeDeterministicRng` in `lib/scoring.ts`.

### 2. Set Party Dietary Preferences and Resolve Conflicts — *Sebastian_Use_Cases.md*, UC19
This is a near-exact narrative translation of `mergeConstraints` in `lib/party.ts`, right down to the specific "vegan diet + 3 or more blocked allergens" conflict threshold, which no other file reproduced correctly.

### 3. Vote to Keep or Reroll a Slot — *Sebastian_Use_Cases.md*, UC18
The only use case in any file that accurately describes the vote/quorum mechanic actually implemented in `PartyClient.tsx` (`maybeActOnVotes`, `quorum = floor(n/2)+1` of currently live peers) — most other lists either omit voting entirely or describe party spins as a single host action.

### 4. Spin the Party Slot Machine — *Carlos_Use_Cases_Claude.md*, UC-17
Verified line-for-line against `app/api/party/spin/route.ts`: it correctly states the system retries the internal `/api/spin` call up to 6 times to fill three unique slots and falls back to a hardcoded 6-dish menu if that call fails — an unusually precise catch of an internal resilience mechanism.

### 5. Lock a Reel and Re-Spin — *Carlos_Use_Cases_Claude.md*, UC-02
Correctly calls out that the legacy "lock by index number only" payload format is silently ignored by the server, matching the Zod union type in `app/api/spin/route.ts`'s request schema — a subtle backward-compatibility detail no other document caught.

### 6. Update Display Name — *Carlos_Use_Cases_Claude.md*, UC-13
Accurately describes the account page's 2-second polling loop against Stack Auth to detect a display-name change and push it into the app's own `User` table — a real, somewhat unusual synchronization design that is easy to miss without reading the component.

### 7. View Recipe Videos for a Dish — *Carlos_Use_Cases_Claude.md*, UC-09
Correctly notes the YouTube lookup is capped at two results per dish and degrades to deterministic stub videos when `YOUTUBE_API_KEY` is unset, matching `lib/youtube.ts` and giving a concrete, verifiable number rather than a vague "some results."

### 8. Save a Meal to Favorites — *Sebastian_Use_Cases.md*, UC5
Correctly distinguishes the guest path (localStorage only) from the authenticated path (DB via `updateUserDetails`) and flags the real gap that a guest's saved meals are not migrated after later signing in.

### 9. Filter Meals by Allergen — *Sebastian_Use_Cases.md*, UC3
Frames allergen exclusion as safety-critical rather than a mere preference, matching the exclude-if-any-match logic in `lib/dishes.ts`, and correctly notes the fallback to a placeholder dish rather than a hard failure when a category is exhausted.

### 10. Register an Account — *Carlos_Use_Cases_Claude.md*, UC-10
Accurately reflects the upsert-by-`auth_id` semantics of account creation (an existing record is reused rather than duplicated) and correctly treats a missing `auth_id` as a null-returning failure rather than a thrown exception.

### 11. Spin for Meal Suggestions — *Karthik_USE_CASES.md*, UC9
The cleanest "what, not how" happy-path of all the solo-spin variants, with extensions that map one-to-one onto real behavior (empty-slot placeholder, cooldown rejection, non-fatal history-write failure) without inventing anything.

### 12. Reach Party Meal Decision — *Karthik_USE_CASES.md*, UC20
The most complete single use case in any document — it ties together categories, merged constraints, voting/quorum, chat, and the implicit host handoff when the host disconnects into one coherent group-decision lifecycle instead of splitting it into disconnected fragments.

### 13. Update Preferences — *Carlos_Use_Cases_Qwen3_8b.md*, UC5
One of the more grounded entries from this file: it correctly reflects that `/api/party/update` returns merged constraints together with a conflict flag and suggestions, matching the actual response shape of `mergeConstraints`.

### 14. Leave a Party — *Sebastian_Use_Cases.md*, UC16
Correctly states there is no explicit host-reassignment step — the next connected member simply becomes host once presence updates — matching `PartyClient.tsx`'s `hostId = livePeers.find(creator) ?? livePeers[0]` logic rather than inventing an explicit "transfer host" action.

### 15. Find Nearby Restaurants After Spinning — *Carlos_Use_Cases_Claude.md*, UC-08
Correctly isolates failure per cuisine (one cuisine's Places error doesn't block the others) and separately handles a failed geocode of the location hint by omitting distance rather than failing the whole request — both real behaviors in `app/api/places/route.ts`.

### 16. Create Party — *Karthik_USE_CASES.md*, UC16
Accurately captures that a signed-in host's saved allergens seed their initial party preferences automatically, and correctly frames cross-device sync as conditional on realtime configuration rather than guaranteed.

### 17. Join Party — *Carlos_Use_Cases_Qwen3_8b.md*, UC1
Despite this file's general weaknesses, this entry correctly reflects that a joining user without stated preferences is simply given empty/default preferences rather than being blocked, matching `app/api/party/join/route.ts`.

### 18. Exchange Realtime Party Messages — *D2_Cameron_Gemini_use_cases.md*, UC9
Accurately reflects the local-echo-then-broadcast pattern in `PartyClient.tsx`'s `sendChat` (the sender sees their own message immediately, independent of the realtime round trip) and correctly treats an empty message as a silent no-op.

### 19. Exclude Allergens — *Karthik_USE_CASES.md*, UC7
Precisely captures that exhausting all candidates for one slot only affects that slot (it shows "no option") rather than failing the whole spin request — an important distinction the scoring engine actually enforces per-reel.

### 20. Chat with Party Members — *Sebastian_Use_Cases.md*, UC20
Correctly identifies the most important limitation of the realtime layer: without `NEXT_PUBLIC_WS_URL` configured, chat (and all party sync) falls back to `BroadcastChannel`, which only reaches other tabs on the same machine — not other devices — a real and easy-to-miss constraint in `lib/realtime.ts`.
