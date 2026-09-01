# MealSlot — Final Top 20 Use Cases

This version uses `Top_20_Use_Cases_Full (1).md` as the canonical Sebastian-based baseline. Every nonduplicate use case is preserved; only duplicate entries are replaced with distinct use cases selected from the team's combined submissions.

## 1. Spin for a Meal

| Part | What it says |
|---|---|
| Name | Spin for a meal |
| Primary actor | Player (Guest or Authenticated User) |
| Stakeholders & interests | Player: wants a fast, low-effort meal decision. |
| Preconditions | App is loaded; dish catalog is populated; spin cooldown has elapsed. |
| Trigger | Player clicks "Spin". |
| Main success scenario | 1. Player selects a category for each of the three slots (or picks a preset).<br>2. Player optionally sets allergen filters and Power-Ups.<br>3. Player clicks Spin.<br>4. System fetches eligible dishes per slot, honoring category, tag, and allergen filters.<br>5. System runs a weighted random selection per slot, respecting any locked slots.<br>6. System displays the three chosen dishes.<br>7. System starts a cooldown before another spin is allowed. |
| Extensions | 4a: No category resolved for a slot → system rejects the spin with "category is required"; player picks a category and retries.<br>4b: No dishes match the active filters for a slot → system fills that slot with a "No options" placeholder dish instead of failing.<br>5a: A slot was locked, but the locked dish no longer matches the current filters → system silently drops the lock and selects a new dish for that slot.<br>5b: Player re-spins with identical filters and reel contents within the same 10-second window as the prior spin → the weighted-random seed repeats and the same result is returned.<br>6a: The spin request errors on the server → system shows placeholder results; player may retry.<br>7a: Player clicks Spin again before the cooldown expires → the control is disabled and no request is sent. |
| Postconditions | Three dishes are displayed for the round; a spin record is logged best-effort; any still-valid locks are retained for the next spin. |

---

## 2. Set Party Dietary Preferences and Resolve Conflicts

| Part | What it says |
|---|---|
| Name | Set dietary preferences for the party |
| Primary actor | Party Member |
| Stakeholders & interests | All party members — need a spin result that every member can actually eat. |
| Preconditions | Player is a connected party member. |
| Trigger | Member opens the party sidebar and sets diet type, allergens, or budget/time preference. |
| Main success scenario | 1. Member opens their preference panel in the party sidebar.<br>2. Member selects a diet type, allergens to avoid, and a budget/time band.<br>3. System sends the updated preferences to the party.<br>4. System merges the member's preferences with everyone else's: strictest compatible diet, union of allergens, minimum budget/time band.<br>5. System stores the merged party-wide constraints.<br>6. Future spins for the party honor the merged constraints. |
| Extensions | 3a: The update request fails on the server → system shows an error and the prior merged constraints remain in effect.<br>4a: The merged diet restrictions become mutually incompatible (no diet satisfies every member) → system flags a conflict and suggests defaulting to vegetarian.<br>4b: A merged vegan diet combines with three or more commonly-blocked allergens → system flags a conflict and suggests relaxing some restrictions. |
| Postconditions | The party's constraints reflect all members' combined preferences (or a flagged conflict with a suggested resolution) and are applied to subsequent spins. |

---

## 3. Vote on a Spin Result

| Part | What it says |
|---|---|
| Name | Vote on a spin result |
| Primary actor | Party Member |
| Stakeholders & interests | Host — executes the group's decision. Other members — want their vote to count toward the outcome. |
| Preconditions | The party has completed a group spin; player is a connected member. |
| Trigger | Member clicks "Keep" or "Reroll" on a slot. |
| Main success scenario | 1. Member views the current dish in a slot.<br>2. Member clicks "Keep" or "Reroll".<br>3. System records the member's vote for that slot.<br>4. System tallies live votes against currently connected members.<br>5. When "keep" votes reach a majority of connected members, system locks that slot automatically.<br>6. When "reroll" votes instead reach a majority, system triggers the host to re-roll just that slot.<br>7. The updated slot state is broadcast to all members. |
| Extensions | 2a: Member changes their vote before quorum is reached → the previous vote is replaced by the new one.<br>4a: A voting member disconnects → once their heartbeat times out, they are dropped from the live count used for quorum, which can shift the threshold needed. |
| Postconditions | The slot's lock/reroll state reflects the group's majority decision without the host needing to act unilaterally. |

---

## 4. Spin the Party Slot Machine

| Part | What it says |
|---|---|
| Name | Spin the party slot machine |
| Primary actor | Party host |
| Stakeholders & interests | All party members — want a fair, allergen-safe result; System — must apply merged constraints |
| Preconditions | Party is active; at least one member has submitted preferences; merged constraints are available |
| Trigger | Host clicks Spin in party mode |
| Main success scenario | 1. Host clicks Spin.<br>2. Client sends `{ code, categories, locked, powerups, constraints }` to `/api/party/spin`.<br>3. System applies merged party constraints (union of all members' allergens and tags).<br>4. System calls the internal `/api/spin` endpoint up to 6 times to fill three unique slots.<br>5. System deduplicates dishes across slots.<br>6. System returns a guaranteed triple of dishes.<br>7. Result is displayed to all party members. |
| Extensions | 2a: No categories provided → system defaults to `["dinner"]`.<br>3a: A slot is locked → the existing dish is retained; only unlocked slots are re-spun.<br>4a: Internal `/api/spin` call fails or times out → system falls back to a hardcoded menu of 6 dishes.<br>5a: After 6 attempts, a slot still has no unique dish → slot receives a "No options" placeholder. |
| Postconditions | Three unique, allergen-safe dishes are selected and displayed to all members |

---

## 5. Lock a Reel and Re-Spin

| Part | What it says |
|---|---|
| Name | Lock a reel and re-spin |
| Primary actor | Solo user |
| Stakeholders & interests | Solo user — wants to keep one dish they like while exploring alternatives for the others |
| Preconditions | A spin has already produced a selection; at least one reel is unlocked |
| Trigger | User locks one or more reels and clicks Spin |
| Main success scenario | 1. User toggles the lock icon on one or more reel cards.<br>2. User clicks Spin.<br>3. System receives the spin request with locked entries `{ index, dishId }`.<br>4. System keeps the locked dish IDs in their slots unchanged.<br>5. System builds fresh candidate lists only for unlocked slots.<br>6. System deduplicates across the full selection including locked dishes.<br>7. Updated selection is returned and displayed. |
| Extensions | 3a: Lock payload contains only index numbers (legacy format) → system ignores them and treats slots as unlocked.<br>5a: No alternative dish exists for an unlocked slot's category → slot receives a placeholder.<br>6a: Deduplication produces fewer than three unique dishes → remaining slots show whatever is available. |
| Postconditions | Locked reels retain their previous dish; unlocked reels display new, deduplicated suggestions |

---

## 6. Update Display Name

| Part | What it says |
|---|---|
| Name | Update display name |
| Primary actor | Authenticated user |
| Stakeholders & interests | System — must keep the Stack Auth display name in sync with the application database |
| Preconditions | User is signed in and on the Account page |
| Trigger | User changes their display name in Stack's AccountSettings widget |
| Main success scenario | 1. User edits their display name in the AccountSettings widget.<br>2. Account page polls Stack Auth every 2 seconds and detects the name change.<br>3. System calls `updateUserDetails` with `{ name: newDisplayName }`.<br>4. Server updates the `User.name` column.<br>5. `UserContext.refreshUser` is called; the header re-renders with the new name. |
| Extensions | 2a: Display name has not changed since last poll → no database call is made.<br>3a: Stack Auth returns no display name → sync is skipped for that poll cycle.<br>4a: Database update fails → error is logged; the displayed name reverts to the previously synced value on the next successful poll. |
| Postconditions | The new name is reflected in the application database and in the page header |

---

## 7. View Recipe Videos for a Dish

| Part | What it says |
|---|---|
| Name | View recipe videos for a dish |
| Primary actor | Solo user |
| Stakeholders & interests | User — wants step-by-step cooking guidance; YouTube API — is the video source |
| Preconditions | A spin result is displayed |
| Trigger | User clicks "Cook at Home" |
| Main success scenario | 1. User clicks "Cook at Home."<br>2. Client opens the recipe video modal.<br>3. Client sends spun dish names to `/api/videos`.<br>4. System searches YouTube for "\<dish\> recipe" for each dish (up to 2 results each).<br>5. System normalizes results: video ID, title, description, URL, thumbnail.<br>6. Modal displays video cards grouped by dish. |
| Extensions | 4a: `YOUTUBE_API_KEY` is not set → system returns deterministic stub videos with a notice; modal still opens with stub content.<br>4b: YouTube API returns an HTTP error for a dish → that dish's video list is empty; per-dish error is recorded; other dishes succeed.<br>6a: No videos found for a dish → that dish's section shows no cards. |
| Postconditions | A modal opens showing recipe video links for each spun dish |

---

## 8. Save a Meal to Favorites

| Part | What it says |
|---|---|
| Name | Save a meal to favorites |
| Primary actor | Player |
| Stakeholders & interests | Authenticated user: wants the saved meal available later, across sessions. Guest: wants short-term, session-only convenience. |
| Preconditions | A spin has produced a displayed dish. |
| Trigger | Player clicks the heart/save icon on a dish. |
| Main success scenario | 1. Player clicks the heart icon on a displayed dish.<br>2. System marks the dish as saved.<br>3. If the player is authenticated, system persists the saved dish to their account.<br>4. If the player is a guest, system stores the saved dish in browser local storage only.<br>5. Player can later view the dish on the Favorites page. |
| Extensions | 3a: The persistence request fails → system shows an error and reverts the heart icon to unsaved.<br>4a: A guest later signs in → the guest's locally saved meals are not migrated to the new account and are effectively lost. |
| Postconditions | The dish appears in Favorites for the current session (guest) or account (authenticated user). |

---

## 9. Filter Meals by Allergen

| Part | What it says |
|---|---|
| Name | Filter meals by allergen |
| Primary actor | Player |
| Stakeholders & interests | Player with a food allergy: needs excluded dishes to never appear (safety-critical, not just preference). |
| Preconditions | Filter menu is available; allergen options are loaded. |
| Trigger | Player opens the filter menu and selects one or more allergens to avoid. |
| Main success scenario | 1. Player opens the Filter Menu.<br>2. System displays available allergen and tag options drawn from the dish catalog plus a default list.<br>3. Player selects allergens to avoid.<br>4. System excludes any dish containing a selected allergen from all future spins.<br>5. Player spins; results contain no dishes with the excluded allergens. |
| Extensions | 2a: The allergen list cannot be derived from the catalog → system falls back to a static default allergen list.<br>4a: The selected allergens eliminate every dish for a slot's category → system fills that slot with a placeholder "No options" dish.<br>5a: Player is signed in and already has allergens saved on their account → system pre-selects those in the filter menu on open. |
| Postconditions | Only allergen-safe dishes are eligible for subsequent spins this session. |

---

## 10. Register an Account

| Part | What it says |
|---|---|
| Name | Register an account |
| Primary actor | New user |
| Stakeholders & interests | System — must create a linked `User` record in the database for future personalization |
| Preconditions | User does not have an existing account |
| Trigger | User completes the Stack Auth sign-up flow |
| Main success scenario | 1. User navigates to the sign-up page via Stack Auth.<br>2. User provides credentials and completes sign-up.<br>3. Stack Auth creates an identity and issues a session.<br>4. Application calls `ensureUserInDB` with the Stack Auth user ID and display name.<br>5. System upserts a `User` record: new UUID, `auth_id`, display name, empty `allergens`, empty `savedMeals`.<br>6. User is redirected to the home page with a personalized session. |
| Extensions | 4a: `auth_id` is missing or null → `ensureUserInDB` returns null; no DB record is created; an error is logged.<br>5a: A `User` with that `auth_id` already exists (returning user) → upsert skips creation and returns the existing record.<br>5b: Database write fails → error is thrown; user sees an error state; sign-in cannot complete. |
| Postconditions | An authenticated session is established; a `User` row is created in the application database linked to the auth ID |

---

## 11. Apply Power-Ups to Bias Selection

| Part | What it says |
|---|---|
| Name | Apply power-ups to bias selection |
| Primary actor | Player |
| Stakeholders & interests | Player: wants results skewed toward healthier, cheaper, or faster options without losing randomness entirely. |
| Preconditions | Spin screen is loaded. |
| Trigger | Player toggles one or more Power-Ups (Healthy, Cheap, ≤30 min). |
| Main success scenario | 1. Player toggles a Power-Up on.<br>2. System records the active Power-Up.<br>3. Player clicks Spin.<br>4. System weights eligible dishes to favor those matching the active Power-Up.<br>5. System selects dishes from the weighted candidates.<br>6. System displays the results. |
| Extensions | 1a: Player toggles a Power-Up off → system removes that influence from later spins.<br>2a: Player activates several Power-Ups → system combines their scoring effects.<br>4a: No eligible dish matches an active Power-Up → system still selects from the available eligible dishes rather than failing the spin. |
| Postconditions | Active Power-Ups influence subsequent spins until the player changes them. |

---

## 12. Browse Saved Meals

| Part | What it says |
|---|---|
| Name | Browse saved meals |
| Primary actor | Authenticated User |
| Stakeholders & interests | User: wants to revisit saved meal ideas and narrow them by category. MealSlot: must resolve saved identifiers against the current dish catalog. |
| Preconditions | User is signed in and has a MealSlot profile. |
| Trigger | User opens the Favorites page. |
| Main success scenario | 1. System loads the user's saved-meal identifiers.<br>2. System resolves the identifiers against the current dish catalog.<br>3. System displays the saved dishes.<br>4. User selects a meal category.<br>5. System displays only saved dishes in that category. |
| Extensions | 1a: User is not signed in → system explains that sign-in is required and offers authentication.<br>2a: A saved identifier no longer exists in the catalog → system omits that entry while displaying the remaining dishes.<br>2b: Dish catalog loading fails → system reports that saved dish details cannot be loaded.<br>3a: User has no saved meals → system displays an empty-state message.<br>5a: No saved dish matches the selected category → system displays an empty filtered result without altering the saved collection. |
| Postconditions | User has viewed the current saved-meal collection or a category-filtered subset. |

---

## 13. Remove a Saved Meal

| Part | What it says |
|---|---|
| Name | Remove a saved meal |
| Primary actor | Authenticated User |
| Stakeholders & interests | User: wants to remove unwanted ideas from Favorites. MealSlot: must keep the displayed and persisted saved collections consistent. |
| Preconditions | User is signed in and the target dish appears on the Favorites page. |
| Trigger | User chooses to remove a saved dish. |
| Main success scenario | 1. User requests removal of a saved dish.<br>2. System removes the dish from the displayed collection.<br>3. System stores the shortened saved-meal collection in the user's profile.<br>4. System refreshes the profile.<br>5. System displays the resulting saved-meal collection. |
| Extensions | 2a: User removes the final saved dish → system displays the Favorites empty state.<br>3a: Persistence fails → system reports or logs the failure and restores the server's prior collection during refresh.<br>4a: Profile refresh fails → the optimistic removal remains visible until a later successful refresh.<br>5a: Server state differs because of a concurrent update → system displays the server's authoritative collection. |
| Postconditions | On success, the dish is absent from the user's displayed and persistent saved-meal collection. |

---

## 14. Leave a Party

| Part | What it says |
|---|---|
| Name | Leave a party |
| Primary actor | Party Member (host or non-host) |
| Stakeholders & interests | Remaining members — need the party to keep functioning, including gaining a new host if needed. |
| Preconditions | Player is currently in a party. |
| Trigger | Player clicks "Leave Party". |
| Main success scenario | 1. Player clicks "Leave Party".<br>2. System removes the player's membership record.<br>3. System broadcasts the departure to remaining members.<br>4. Player's local party state is cleared and they return to the Party landing screen. |
| Extensions | 2a: The leaving player was the host → no explicit reassignment occurs; the next live member is treated as host once presence updates.<br>2b: Membership removal fails on the server → system shows an error; player may retry leaving. |
| Postconditions | Player no longer appears in the party's member list; if they were host, host duties implicitly pass to another connected member. |

---

## 15. Find Nearby Restaurants After Spinning

| Part | What it says |
|---|---|
| Name | Find nearby restaurants after spinning |
| Primary actor | Solo user |
| Stakeholders & interests | User — wants to eat out; Google Places API — is the data source; System — must resolve location |
| Preconditions | A spin result with at least one dish is displayed |
| Trigger | User clicks "Eat Outside" |
| Main success scenario | 1. User clicks "Eat Outside."<br>2. Browser requests the user's geolocation.<br>3. Client sends cuisine names derived from the spin result along with GPS coordinates to `/api/places`.<br>4. System queries Google Places text search for each cuisine near the provided coordinates.<br>5. System normalizes results: name, address, rating, price tier, distance (km), Google Maps URL.<br>6. Client displays venue cards and renders pins on the embedded map. |
| Extensions | 2a: User denies geolocation → client calls `/api/places` without coordinates.<br>2b: Browser does not support geolocation → same as 2a.<br>3a: No coordinates provided → system geocodes the `locationHint` ("Denver") to obtain an origin.<br>3b: Geocoding fails → distances are omitted; venues are still returned with a notice.<br>4a: Google Places returns an error for a cuisine → that cuisine's result is empty; other cuisines succeed; per-cuisine errors are collected and returned. |
| Postconditions | A list of nearby restaurants matching the spun cuisines is displayed with ratings, prices, distances, and map |

---

## 16. Create Party

| Part | What it says |
|---|---|
| Name | Create party |
| Primary actor | Party host |
| Stakeholders & interests | Host: establish a shared meal-decision session. Invitees: receive a valid room to join. MealSlot: create a unique active party and identify its host. |
| Preconditions | Host is in party mode and has supplied a nickname. |
| Trigger | Host requests a new party. |
| Main success scenario | 1. System validates the host nickname.<br>2. System creates an active party with a six-character code.<br>3. System adds the creator as the first party member and host.<br>4. System initializes the host's party preferences.<br>5. System displays the active party code and collaborative experience.<br>6. System establishes live presence for the host. |
| Extensions | 1a: Nickname is empty or invalid → system prevents party creation.<br>2a: Generated code collides with an existing party → system retries or reports creation failure.<br>2b: Party storage fails → system reports that the party could not be created.<br>4a: Host has saved account allergens → system initializes party allergens from that profile.<br>6a: Cross-device realtime is not configured → system uses same-origin browser communication only. |
| Postconditions | An active party exists with a unique code, and the creator is its host member. |

---

## 17. Join Party

| Part | What it says |
|---|---|
| Name | Join Party |
| Primary actor | User |
| Stakeholders & interests | User: Join an existing party using a 6-character code and be associated with the party. Host: Manage party members, preferences, and interactions. System: Maintain accurate party member records and preferences. Party Member: Update diet preferences and allergens, and be recognized in the member list. |
| Preconditions | User has a valid auth_id. |
| Trigger | User provides a 6-character party code and optionally a nickname. |
| Main success scenario | 1. User provides a 6-character party code.<br>2. System verifies the party code exists.<br>3. System associates the user with the party using their auth_id.<br>4. System creates a party member record with the user's preferences.<br>5. System returns the party ID, member ID, and party code.<br>6. System displays the user's nickname and 'you' indicator in the member list. |
| Extensions | 2a: Party code is invalid or does not exist → system returns an error indicating the party code is invalid.<br>4a: User already belongs to a party → system returns an error indicating the user is already part of a party.<br>5a: User provides a nickname → system stores the nickname for the user in the party member record.<br>6a: User has not provided any preferences → system stores default preferences for the user in the party member record. |
| Postconditions | User is associated with the party and has a party member record; user's nickname and preferences are stored in the party member record; user is displayed in the member list with 'you' indicator. |

---

## 18. Sign In to an Account

| Part | What it says |
|---|---|
| Name | Sign in to an account |
| Primary actor | Returning User |
| Stakeholders & interests | User: wants saved meals and allergen preferences restored. Authentication provider: must validate identity securely. MealSlot: must load only the matching user's profile. |
| Preconditions | User has an existing account and is currently signed out. |
| Trigger | User clicks Sign In. |
| Main success scenario | 1. System presents the available sign-in methods.<br>2. User authenticates with a registered identity.<br>3. Authentication provider validates the identity and establishes a session.<br>4. MealSlot locates the linked application profile.<br>5. System loads the user's saved meals and allergen preferences.<br>6. System returns the user to the application in the signed-in state. |
| Extensions | 2a: User requests password recovery → authentication provider begins its recovery flow.<br>3a: Credentials are invalid → system displays an authentication error and creates no session.<br>3b: A third-party sign-in provider fails → system reports the failure and permits another supported method.<br>4a: No application profile exists for the valid identity → MealSlot creates one with empty saved data before continuing.<br>5a: Profile loading fails → system reports the error and does not expose stale or another user's account data. |
| Postconditions | User has an authenticated session with their own saved meals and preferences loaded. |

---

## 19. Sign Out of an Account

| Part | What it says |
|---|---|
| Name | Sign out of an account |
| Primary actor | Authenticated User |
| Stakeholders & interests | User: wants to end access on the current device. MealSlot: must prevent a later user from seeing cached personal data. |
| Preconditions | User is signed in. |
| Trigger | User clicks Sign Out. |
| Main success scenario | 1. User requests sign-out.<br>2. Authentication provider ends the current session.<br>3. System clears the in-app user profile state.<br>4. System clears account-specific client caches.<br>5. System returns the visitor to the signed-out home experience. |
| Extensions | 2a: Provider sign-out fails → system reports the failure and does not falsely claim that the session ended.<br>3a: Client storage is unavailable → system clears removable in-memory state and relies on the ended provider session for protection.<br>5a: Visitor directly opens an account-only page after sign-out → system requires authentication and exposes no previous user's data. |
| Postconditions | No authenticated session remains in the current browser context and prior account data is not exposed. |

---

## 20. Chat with Party Members

| Part | What it says |
|---|---|
| Name | Chat with party members |
| Primary actor | Party Member |
| Stakeholders & interests | Other members — want to coordinate the group's decision in real time. |
| Preconditions | Player is a connected party member. |
| Trigger | Member types a message and clicks "Send" in the party chat. |
| Main success scenario | 1. Member types a message in the chat panel.<br>2. Member sends the message.<br>3. System broadcasts the message to all connected party members.<br>4. All members see the message appear in their chat panel with the sender's nickname. |
| Extensions | 2a: The message is empty → the send action does nothing.<br>3a: No dedicated realtime server is configured for the party → the message only reaches other browser tabs on the same machine, not members on other devices. |
| Postconditions | The message is visible in the chat history of all currently connected members for the remainder of the session; it is not persisted. |