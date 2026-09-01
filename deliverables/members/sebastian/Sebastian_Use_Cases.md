# MealSlot — Use Cases

Twenty use cases covering the MealSlot application (solo meal-decision "slot machine", party/group mode, account and favorites management). Derived from the actual behavior implemented in `proj2/mealslot` (Next.js app, `app/api/*` route handlers, `lib/scoring.ts`, `lib/party.ts`, `lib/dishes.ts`, `lib/allergens.ts`, `PartyClient.tsx`, `SlotMachine.tsx`).

Actors referenced throughout:
- **Guest** — unauthenticated player; state lives only in the browser.
- **Authenticated User** — signed in via Stack Auth; has a persisted account.
- **Party Host** — the party member currently recognized as host (derived live from presence, not a fixed role).
- **Party Member** — any player connected to a party, host or not.

---

## 1. Spin for a Meal

| Part | Detail |
|---|---|
| Name | Spin for a meal |
| Primary actor | Player (Guest or Authenticated User) |
| Stakeholders & interests | Player: wants a fast, low-effort meal decision. |
| Preconditions | App is loaded; dish catalog is populated; spin cooldown has elapsed. |
| Trigger | Player clicks "Spin". |
| Main success scenario | 1. Player selects a category for each of the three slots (or picks a preset).<br>2. Player optionally sets allergen filters and Power-Ups.<br>3. Player clicks Spin. <br>4. System fetches eligible dishes per slot, honoring category, tag, and allergen filters. <br>5. System runs a weighted random selection per slot, respecting any locked slots. <br>6. System displays the three chosen dishes. <br>7. System starts a cooldown before another spin is allowed. |
| Extensions | 4a. No category resolved for a slot → system rejects the spin with "category is required"; player picks a category and retries.<br>4b. No dishes match the active filters for a slot → system fills that slot with a "No options" placeholder dish instead of failing.<br>5a. A slot was locked, but the locked dish no longer matches the current filters → system silently drops the lock and selects a new dish for that slot.<br>5b. Player re-spins with identical filters and reel contents within the same 10-second window as the prior spin → the weighted-random seed repeats and the same result is returned.<br>6a. The spin request errors on the server → system shows placeholder results; player may retry.<br>7a. Player clicks Spin again before the cooldown expires → the control is disabled and no request is sent. |
| Postconditions | Three dishes are displayed for the round; a spin record is logged best-effort; any still-valid locks are retained for the next spin. |

## 2. Lock a Dish and Re-Spin

| Part | Detail |
|---|---|
| Name | Lock a dish and re-spin |
| Primary actor | Player |
| Stakeholders & interests | Player: wants to keep a favored pick while re-rolling the rest. |
| Preconditions | A spin has completed and results are displayed. |
| Trigger | Player clicks the lock icon on a reel showing a dish they want to keep. |
| Main success scenario | 1. Player clicks lock on a slot. <br>2. System marks that slot locked. <br>3. Player clicks Spin. <br>4. System re-spins only the unlocked slots. <br>5. System keeps the locked dish in place and displays new results for the other slots. |
| Extensions | 1a. Player unlocks a previously locked slot → the lock is removed and the slot is included in the next spin.<br>4a. Filters changed since the lock was set and the locked dish no longer matches them → system silently drops the lock and selects a new dish for that slot instead of keeping it. |
| Postconditions | The locked dish (if still valid) persists across the spin; unlocked slots show newly selected dishes. |

## 3. Filter Meals by Allergen

| Part | Detail |
|---|---|
| Name | Filter meals by allergen |
| Primary actor | Player |
| Stakeholders & interests | Player with a food allergy: needs excluded dishes to never appear (safety-critical, not just preference). |
| Preconditions | Filter menu is available; allergen options are loaded. |
| Trigger | Player opens the filter menu and selects one or more allergens to avoid. |
| Main success scenario | 1. Player opens the Filter Menu. <br>2. System displays available allergen and tag options drawn from the dish catalog plus a default list. <br>3. Player selects allergens to avoid. <br>4. System excludes any dish containing a selected allergen from all future spins. <br>5. Player spins; results contain no dishes with the excluded allergens. |
| Extensions | 2a. The allergen list cannot be derived from the catalog → system falls back to a static default allergen list.<br>4a. The selected allergens eliminate every dish for a slot's category → system fills that slot with a placeholder "No options" dish.<br>5a. Player is signed in and already has allergens saved on their account → system pre-selects those in the filter menu on open. |
| Postconditions | Only allergen-safe dishes are eligible for subsequent spins this session. |

## 4. Apply Power-Ups to Bias Selection

| Part | Detail |
|---|---|
| Name | Apply power-ups to bias selection |
| Primary actor | Player |
| Stakeholders & interests | Player: wants results skewed toward healthier, cheaper, or faster options without losing randomness entirely. |
| Preconditions | Spin screen is loaded. |
| Trigger | Player toggles one or more Power-Ups (Healthy, Cheap, ≤30 min). |
| Main success scenario | 1. Player toggles a Power-Up on. <br>2. System records the active Power-Up(s). <br>3. Player spins. <br>4. System weights dish selection to favor dishes matching the active Power-Up(s). <br>5. Results reflect the bias. |
| Extensions | 1a. Player toggles a Power-Up off → weighting for that attribute returns to neutral for future spins.<br>4a. No dish in a slot's eligible set strongly matches the Power-Up criteria → system still selects from the available (lower-weighted) dishes rather than failing the spin. |
| Postconditions | Active Power-Up state persists for subsequent spins until toggled off. |

## 5. Save a Meal to Favorites

| Part | Detail |
|---|---|
| Name | Save a meal to favorites |
| Primary actor | Player |
| Stakeholders & interests | Authenticated user: wants the saved meal available later, across sessions. Guest: wants short-term, session-only convenience. |
| Preconditions | A spin has produced a displayed dish. |
| Trigger | Player clicks the heart/save icon on a dish. |
| Main success scenario | 1. Player clicks the heart icon on a displayed dish. <br>2. System marks the dish as saved. <br>3. If the player is authenticated, system persists the saved dish to their account. <br>4. If the player is a guest, system stores the saved dish in browser local storage only. <br>5. Player can later view the dish on the Favorites page. |
| Extensions | 3a. The persistence request fails → system shows an error and reverts the heart icon to unsaved.<br>4a. A guest later signs in → the guest's locally saved meals are not migrated to the new account and are effectively lost. |
| Postconditions | The dish appears in Favorites for the current session (guest) or account (authenticated user). |

## 6. Remove a Saved Meal

| Part | Detail |
|---|---|
| Name | Remove a saved meal |
| Primary actor | Authenticated User |
| Stakeholders & interests | User: wants to curate their favorites list over time. |
| Preconditions | User is signed in and has at least one saved meal. |
| Trigger | User clicks "remove" on an item on the Favorites page. |
| Main success scenario | 1. User navigates to the Favorites page. <br>2. System lists saved meals, optionally filtered by category. <br>3. User clicks remove on a meal. <br>4. System removes the dish ID from the user's saved list. <br>5. System persists the updated list to the account. <br>6. The updated list is displayed without the removed meal. |
| Extensions | 1a. User is not signed in → system shows a "Sign In" prompt instead of the favorites list.<br>2a. User has no saved meals → system displays an empty state.<br>5a. Persistence fails on the server → system shows an error and the meal reappears in the list. |
| Postconditions | The removed dish no longer appears in the user's saved meals, in this and future sessions. |

## 7. View Recipe and Cooking Videos ("Cook at Home")

| Part | Detail |
|---|---|
| Name | View recipe and cooking videos |
| Primary actor | Player |
| Stakeholders & interests | Player: wants to actually cook the spun dish at home. |
| Preconditions | A spin has produced displayed dishes. |
| Trigger | Player clicks "Cook at Home" for a dish. |
| Main success scenario | 1. Player clicks "Cook at Home". <br>2. System requests a recipe (ingredients and steps) for the dish. <br>3. System requests matching cooking videos for the dish. <br>4. System displays a modal with the recipe and video links. |
| Extensions | 2a. No recipe-generation key is configured on the server → system returns a deterministic stub recipe instead of an AI-generated one, with no visible error.<br>3a. No video-search key is configured → system returns stub video placeholders along with a notice.<br>3b. Video search fails for a specific dish → system omits videos for that dish but still shows the recipe and any other dishes' videos. |
| Postconditions | Player has viewed a recipe and video options for the dish; nothing is persisted. |

## 8. Find Nearby Restaurants ("Eat Outside")

| Part | Detail |
|---|---|
| Name | Find nearby restaurants |
| Primary actor | Player |
| Stakeholders & interests | Player: wants to eat the spun dish out rather than cook it. Restaurants: want customers to order food that they enjoy. |
| Preconditions | A spin has produced displayed dishes. |
| Trigger | Player clicks "Eat Outside". |
| Main success scenario | 1. Player clicks "Eat Outside". <br>2. System requests the player's geolocation. <br>3. Player grants location access. <br>4. System searches for nearby restaurants matching the dishes' cuisines. <br>5. System displays a list and map of nearby venues with distances. |
| Extensions | 3a. Player denies or lacks geolocation → system falls back to a default city and omits distance from results.<br>4a. No Places API key is configured on the server → system returns a "missing key" notice for that cuisine instead of results.<br>4b. The search for one cuisine fails → system still returns results for the other cuisines, collecting the failure separately rather than failing the whole request. |
| Postconditions | Player sees a list/map of nearby venues, or an explanatory notice where results are unavailable. |

## 9. Sign Up for an Account

| Part | Detail |
|---|---|
| Name | Sign up for an account |
| Primary actor | Guest |
| Stakeholders & interests | Guest: wants saved meals and preferences to persist across devices and sessions. |
| Preconditions | Guest is on the site and not authenticated. |
| Trigger | Guest clicks "Sign Up". |
| Main success scenario | 1. Guest clicks "Sign Up". <br>2. System presents sign-up options (Google, GitHub, email/password). <br>3. Guest completes sign-up with the chosen method. <br>4. System authenticates the new identity. <br>5. System creates a corresponding account record in the app's database. <br>6. Guest is redirected back into the app as a signed-in user. |
| Extensions | 3a. Guest cancels sign-up mid-flow → returned to the app still as a guest, no account created.<br>3b. Email is already registered → system shows an error and suggests signing in instead.<br>5a. Account record creation fails after authentication succeeds → system shows an error; player may retry. |
| Postconditions | A new authenticated account exists, linked to the player's chosen identity provider. |

## 10. Sign In to an Account

| Part | Detail |
|---|---|
| Name | Sign in to an account |
| Primary actor | Returning User |
| Stakeholders & interests | User: wants their saved meals and preferences restored. |
| Preconditions | User already has an account. |
| Trigger | User clicks "Sign In". |
| Main success scenario | 1. User clicks "Sign In". <br>2. System presents sign-in options. <br>3. User authenticates with the chosen method. <br>4. System verifies the identity. <br>5. System loads the user's saved meals and allergen preferences into the app. <br>6. User is redirected back into the app in the signed-in state. |
| Extensions | 3a. Incorrect credentials are entered → system shows an error; user retries.<br>5a. No prior app record exists for this identity → system creates one on the fly with empty preferences. |
| Postconditions | User is signed in; their saved meals and preferences are available for the session. |

## 11. Sign Out

| Part | Detail |
|---|---|
| Name | Sign out of an account |
| Primary actor | Authenticated User |
| Stakeholders & interests | Authenticated User: wants to end their session, e.g. on a shared device. |
| Preconditions | User is signed in. |
| Trigger | User clicks "Sign Out". |
| Main success scenario | 1. User clicks "Sign Out". <br>2. System ends the authenticated session. <br>3. System clears in-app user state. <br>4. User is returned to guest mode on the home page. |
| Extensions | 2a. The sign-out request fails (e.g. network error) → system shows an error and the user remains signed in until they retry. |
| Postconditions | No authenticated session remains; the player continues as a guest with no persisted saves. |

## 12. Manage Dietary Preferences (Allergens)

| Part | Detail |
|---|---|
| Name | Manage dietary preferences |
| Primary actor | Authenticated User |
| Stakeholders & interests | User with food restrictions: wants their allergen list applied automatically to every future spin. |
| Preconditions | User is signed in and viewing the Account page. |
| Trigger | User opens the Dietary Preferences panel. |
| Main success scenario | 1. User navigates to Account → Dietary Preferences. <br>2. System displays available allergens with the user's currently selected ones checked. <br>3. User toggles allergens. <br>4. User saves changes. <br>5. System persists the updated allergen list to the account. <br>6. System applies the updated allergens to future spins automatically. |
| Extensions | 5a. The save request fails → system shows an error and the prior selection remains active. |
| Postconditions | The updated allergen list is stored on the account and pre-applied to all future spins and filters. |

## 13. Update Account Name

| Part | Detail |
|---|---|
| Name | Update account name |
| Primary actor | Authenticated User |
| Stakeholders & interests | User: wants their display name kept current across the app. |
| Preconditions | User is signed in. |
| Trigger | User edits their display name in Account Settings. |
| Main success scenario | 1. User opens Account Settings. <br>2. User edits their display name. <br>3. User saves the change. <br>4. System validates the name is non-empty. <br>5. System updates the name in both the identity provider and the app database. <br>6. The updated name is reflected across the app. |
| Extensions | 4a. Submitted name is blank or whitespace-only → system rejects with a validation error; name is unchanged.<br>5a. The update fails on the server → system shows an error and the prior name remains displayed. |
| Postconditions | The user's display name is updated everywhere it appears in the app. |

## 14. Create a Party

| Part | Detail |
|---|---|
| Name | Create a party |
| Primary actor | Player (becomes Party Host) |
| Stakeholders & interests | Players who will join later — need a working, unique invite code. |
| Preconditions | Player is on the Party page. |
| Trigger | Player enters a nickname and clicks "Create Party". |
| Main success scenario | 1. Player enters a nickname. <br>2. Player clicks "Create Party". <br>3. System generates a unique 6-character party code. <br>4. System registers the player as the first member (host). <br>5. System marks the party active and displays the invite code/link. <br>6. Player enters the party room as host. |
| Extensions | 1a. Nickname is left blank or exceeds 24 characters → system rejects with a validation error.<br>3a. Party creation fails on the server → system shows an error; player may retry. |
| Postconditions | A new active party exists with the creator as its sole member and host, joinable via its code. |

## 15. Join a Party

| Part | Detail |
|---|---|
| Name | Join a party |
| Primary actor | Player |
| Stakeholders & interests | Host and existing members — want a smooth join that doesn't disrupt an in-progress round. |
| Preconditions | Player has a valid party invite code. |
| Trigger | Player enters a code and nickname and clicks "Join". |
| Main success scenario | 1. Player enters a party code and nickname. <br>2. Player clicks "Join". <br>3. System looks up the party by code. <br>4. System verifies the party is active. <br>5. System adds the player as a new member. <br>6. System broadcasts presence so existing members see the new member appear. <br>7. Player enters the party room and sees current members and any in-progress spin state. |
| Extensions | 1a. Nickname is blank or invalid → system rejects with a validation error.<br>4a. Code does not exist or the party is inactive → system responds "not found"; player sees an error and may retry.<br>7a. A spin is already in progress or completed → the newcomer requests a state sync from the host and receives the current reel results. |
| Postconditions | Player is a member of the party and visible to other members in real time. |

## 16. Leave a Party

| Part | Detail |
|---|---|
| Name | Leave a party |
| Primary actor | Party Member (host or non-host) |
| Stakeholders & interests | Remaining members — need the party to keep functioning, including gaining a new host if needed. |
| Preconditions | Player is currently in a party. |
| Trigger | Player clicks "Leave Party". |
| Main success scenario | 1. Player clicks "Leave Party". <br>2. System removes the player's membership record. <br>3. System broadcasts the departure to remaining members. <br>4. Player's local party state is cleared and they return to the Party landing screen. |
| Extensions | 2a. The leaving player was the host → no explicit reassignment occurs; the next live member is treated as host once presence updates.<br>2b. Membership removal fails on the server → system shows an error; player may retry leaving. |
| Postconditions | Player no longer appears in the party's member list; if they were host, host duties implicitly pass to another connected member. |

## 17. Group Spin (Host-Led)

| Part | Detail |
|---|---|
| Name | Spin for the party |
| Primary actor | Party Host |
| Stakeholders & interests | Party members — want a fair result that all of them see at the same time and that respects everyone's dietary constraints. |
| Preconditions | Player is currently recognized as host of an active party with at least one member. |
| Trigger | Host selects categories and clicks "Spin". |
| Main success scenario | 1. Host selects a category for each slot. <br>2. Host clicks "Spin". <br>3. System spins each unlocked slot, honoring the party's merged allergen, diet, and budget/time constraints. <br>4. System selects three dishes, avoiding duplicates across slots. <br>5. System broadcasts the results to all party members in real time. <br>6. All members see the same three dishes simultaneously. |
| Extensions | 1a. A non-host member attempts to spin → the spin controls are disabled for them. <br>3a. The internal spin pipeline errors for a slot → system substitutes a fallback dish or menu rather than failing; a result is still returned to all members.<br>5a. A member is disconnected when results are broadcast → they receive the result via a state sync when they reconnect. |
| Postconditions | All connected party members see an identical, published set of results for the round. |

## 18. Vote to Keep or Reroll a Slot

| Part | Detail |
|---|---|
| Name | Vote on a spin result |
| Primary actor | Party Member |
| Stakeholders & interests | Host — executes the group's decision. Other members — want their vote to count toward the outcome. |
| Preconditions | The party has completed a group spin; player is a connected member. |
| Trigger | Member clicks "Keep" or "Reroll" on a slot. |
| Main success scenario | 1. Member views the current dish in a slot. <br>2. Member clicks "Keep" or "Reroll". <br>3. System records the member's vote for that slot. <br>4. System tallies live votes against currently connected members. <br>5. When "keep" votes reach a majority of connected members, system locks that slot automatically. <br>6. When "reroll" votes instead reach a majority, system triggers the host to re-roll just that slot. <br>7. The updated slot state is broadcast to all members. |
| Extensions | 2a. Member changes their vote before quorum is reached → the previous vote is replaced by the new one.<br>4a. A voting member disconnects → once their heartbeat times out, they are dropped from the live count used for quorum, which can shift the threshold needed. |
| Postconditions | The slot's lock/reroll state reflects the group's majority decision without the host needing to act unilaterally. |

## 19. Set Party Dietary Preferences and Resolve Conflicts

| Part | Detail |
|---|---|
| Name | Set dietary preferences for the party |
| Primary actor | Party Member |
| Stakeholders & interests | All party members — need a spin result that every member can actually eat. |
| Preconditions | Player is a connected party member. |
| Trigger | Member opens the party sidebar and sets diet type, allergens, or budget/time preference. |
| Main success scenario | 1. Member opens their preference panel in the party sidebar. <br>2. Member selects a diet type, allergens to avoid, and a budget/time band. <br>3. System sends the updated preferences to the party. <br>4. System merges the member's preferences with everyone else's: strictest compatible diet, union of allergens, minimum budget/time band. <br>5. System stores the merged party-wide constraints. <br>6. Future spins for the party honor the merged constraints. |
| Extensions | 3a. The update request fails on the server → system shows an error and the prior merged constraints remain in effect.<br>4a. The merged diet restrictions become mutually incompatible (no diet satisfies every member) → system flags a conflict and suggests defaulting to vegetarian.<br>4b. A merged vegan diet combines with three or more commonly-blocked allergens → system flags a conflict and suggests relaxing some restrictions. |
| Postconditions | The party's constraints reflect all members' combined preferences (or a flagged conflict with a suggested resolution) and are applied to subsequent spins. |

## 20. Chat with Party Members

| Part | Detail |
|---|---|
| Name | Chat with party members |
| Primary actor | Party Member |
| Stakeholders & interests | Other members — want to coordinate the group's decision in real time. |
| Preconditions | Player is a connected party member. |
| Trigger | Member types a message and clicks "Send" in the party chat. |
| Main success scenario | 1. Member types a message in the chat panel. <br>2. Member sends the message. <br>3. System broadcasts the message to all connected party members. <br>4. All members see the message appear in their chat panel with the sender's nickname. |
| Extensions | 2a. The message is empty → the send action does nothing.<br>3a. No dedicated realtime server is configured for the party → the message only reaches other browser tabs on the same machine, not members on other devices. |
| Postconditions | The message is visible in the chat history of all currently connected members for the remainder of the session; it is not persisted. |
