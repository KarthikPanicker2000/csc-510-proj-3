# MealSlot: 20 Main Use Cases

These use cases were reverse engineered from the implemented MealSlot pages, components, route handlers, data model, and tests. They describe user goals and observable behavior rather than implementation mechanisms. Each main success scenario contains only the happy path; alternatives and failures appear under **Extensions**.

## UC1: Create account

| Part | Content |
|---|---|
| **Name** | Create account |
| **Primary actor** | Guest diner |
| **Stakeholders & interests** | Guest diner: obtain a personal account. MealSlot: associate preferences and saved meals with a stable identity. Authentication provider: create and protect the identity. |
| **Preconditions** | Guest is not signed in; the authentication service is available. |
| **Trigger** | Guest decides to register for MealSlot. |
| **Main success scenario** | 1. Guest begins account registration. 2. System presents the available registration methods. 3. Guest supplies a valid identity and completes verification. 4. Authentication provider creates the identity. 5. MealSlot creates the corresponding diner profile. 6. System signs in the new diner and opens account settings. |
| **Extensions** | 3a: Submitted identity data is invalid → authentication provider explains the problem and requests corrected data. 3b: Identity is already registered → system directs the guest to sign in. 4a: Authentication service is unavailable → system leaves the guest unsigned in and reports that registration could not be completed. 5a: MealSlot profile creation fails → authentication succeeds, but system reports or logs the profile synchronization failure. |
| **Postconditions** | A protected authentication identity and corresponding MealSlot diner profile exist; diner is signed in. |

## UC2: Sign in

| Part | Content |
|---|---|
| **Name** | Sign in |
| **Primary actor** | Registered diner |
| **Stakeholders & interests** | Diner: regain personal preferences and saved meals. MealSlot: identify the correct profile. Authentication provider: prevent unauthorized access. |
| **Preconditions** | Diner has a registered identity and is signed out. |
| **Trigger** | Diner requests access to the account. |
| **Main success scenario** | 1. Diner starts sign-in. 2. System presents the available authentication methods. 3. Diner supplies valid credentials. 4. Authentication provider verifies the diner. 5. MealSlot loads and caches the diner profile. 6. System returns the diner to the solo meal experience as signed in. |
| **Extensions** | 3a: Credentials are invalid → authentication provider rejects the attempt and allows another. 4a: Authentication service is unavailable → system keeps the diner signed out. 5a: MealSlot profile does not exist → system attempts to create it from the authenticated identity. 5b: Profile loading fails → system treats the session as having no usable MealSlot profile. |
| **Postconditions** | Diner has an authenticated session and the associated MealSlot profile is available to the application. |

## UC3: Sign out

| Part | Content |
|---|---|
| **Name** | Sign out |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: end access on the current browser. MealSlot: stop exposing personal data. Authentication provider: invalidate or end the session correctly. |
| **Preconditions** | Diner is signed in. |
| **Trigger** | Diner requests to sign out. |
| **Main success scenario** | 1. Diner requests sign-out from the personal menu. 2. System sends the diner through the configured sign-out flow. 3. Authentication provider ends the session. 4. MealSlot clears the active profile from the interface. 5. System returns to the solo experience as a guest. |
| **Extensions** | 2a: No provider sign-out destination is configured → MealSlot clears its local user state and returns home. 3a: Provider sign-out fails → system reports the failure and does not claim that the session ended. |
| **Postconditions** | Personal account controls and profile data are no longer available in the active MealSlot session. |

## UC4: Manage account profile

| Part | Content |
|---|---|
| **Name** | Manage account profile |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: keep identity information current. MealSlot: show a consistent name throughout the application. Authentication provider: securely manage account attributes. |
| **Preconditions** | Diner is signed in and the account settings service is available. |
| **Trigger** | Diner opens account settings. |
| **Main success scenario** | 1. System presents the diner’s account settings. 2. Diner changes an account attribute such as the display name. 3. Authentication provider saves the change. 4. MealSlot synchronizes the updated display name to the diner profile. 5. System displays the updated identity in the application. |
| **Extensions** | 2a: Proposed account data is invalid → account service rejects it and explains the constraint. 3a: Authentication provider cannot save the change → existing account data remains active. 4a: MealSlot profile synchronization fails → provider data is retained, but the application may continue displaying the prior profile value. |
| **Postconditions** | Successfully changed account data is stored by the authentication provider and synchronized to the MealSlot profile. |

## UC5: Save dietary preferences

| Part | Content |
|---|---|
| **Name** | Save dietary preferences |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: avoid unsuitable dishes without re-entering restrictions. MealSlot: generate safer, more relevant suggestions. |
| **Preconditions** | Diner is signed in; a MealSlot profile and allergen catalog are available. |
| **Trigger** | Diner opens the dietary-preferences section of account settings. |
| **Main success scenario** | 1. System shows the available allergens and the diner’s current selections. 2. Diner adds or removes allergen preferences. 3. Diner requests that the selections be saved. 4. System stores the updated preferences in the diner profile. 5. System confirms the save and uses the preferences in later meal filtering. |
| **Extensions** | 1a: Allergen catalog cannot be loaded → system cannot offer a complete selection list. 3a: Diner is no longer authenticated → system does not save the selections. 4a: Storage fails → system reports that preferences were not saved. 4b: Stored preferences contain unknown values → system ignores values that are not in the current allergen catalog. |
| **Postconditions** | Diner profile contains the selected valid allergens, and future meal flows can initialize from them. |

## UC6: Configure meal categories

| Part | Content |
|---|---|
| **Name** | Configure meal categories |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: receive suggestions for the desired meal occasions. MealSlot: know which catalog category belongs on each reel. |
| **Preconditions** | Diner is in solo mode. |
| **Trigger** | Diner decides what kinds of meals the three slots should represent. |
| **Main success scenario** | 1. System presents three meal slots with their current categories. 2. Diner chooses a category for each slot. 3. System records the three-category arrangement. 4. System displays the configured categories as the basis for the next spin. |
| **Extensions** | 2a: Diner chooses a predefined full-day arrangement → system assigns breakfast, lunch, and dinner. 2b: Diner chooses a dinner-and-dessert arrangement → system assigns two dinner slots and one dessert slot. 2c: Diner chooses a same-category preset → system assigns lunch, dessert, or snack to all three slots. |
| **Postconditions** | Each solo slot has a category to use for subsequent meal selection. |

## UC7: Exclude allergens

| Part | Content |
|---|---|
| **Name** | Exclude allergens |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: avoid dishes containing unwanted allergens. MealSlot: honor safety-related constraints during selection. |
| **Preconditions** | Diner is in solo mode; the dish catalog exposes allergen information. |
| **Trigger** | Diner chooses to constrain meal suggestions by allergens. |
| **Main success scenario** | 1. System presents allergens found in the dish catalog. 2. Diner selects the allergens to exclude. 3. System records the active exclusions. 4. System removes dishes containing any selected allergen from later spin candidates. |
| **Extensions** | 1a: Diner has saved allergen preferences → system preselects the valid saved values. 1b: Allergen information cannot be loaded → system shows that filters are unavailable. 4a: Exclusions eliminate every candidate for a slot → the next spin returns no option for that slot. |
| **Postconditions** | Active solo constraints include the diner’s selected allergen exclusions. |

## UC8: Prioritize meal qualities

| Part | Content |
|---|---|
| **Name** | Prioritize meal qualities |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: influence suggestions toward health, price, or preparation-time goals. MealSlot: rank eligible dishes according to stated priorities. |
| **Preconditions** | Diner is preparing a solo spin. |
| **Trigger** | Diner chooses one or more meal priorities. |
| **Main success scenario** | 1. System presents the available priorities: healthy, cheap, and no more than 30 minutes. 2. Diner activates the desired priorities. 3. System records the selected priorities. 4. System increases the selection weight of dishes matching those priorities during the next spin. |
| **Extensions** | 2a: Diner deactivates a priority → system removes that influence from later spins. 4a: No eligible dish matches a priority → system selects from the remaining eligible dishes without guaranteeing that quality. |
| **Postconditions** | The active power-up settings influence subsequent solo meal selection. |

## UC9: Spin for meal suggestions

| Part | Content |
|---|---|
| **Name** | Spin for meal suggestions |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: quickly obtain varied meal ideas. MealSlot: apply categories and constraints consistently while avoiding duplicate results. |
| **Preconditions** | Diner is in solo mode; all three slots have categories; spin cooldown has expired. |
| **Trigger** | Diner requests a spin. |
| **Main success scenario** | 1. System collects the configured categories, exclusions, priorities, and locked selections. 2. System identifies eligible dishes for each slot. 3. System selects a weighted set of dishes. 4. System removes duplicate selections. 5. System displays the resulting meal choices. 6. System prepares related cooking-video suggestions and starts a short spin cooldown. |
| **Extensions** | 2a: A slot has no eligible dish → system displays “No options” for that slot. 3a: Spin request is invalid → system rejects it and reports the problem. 3b: Meal selection fails internally → system reports that the spin failed. 5a: Recording the spin history fails → system still returns and displays the selected dishes. 6a: Diner requests another spin during cooldown → system prevents the request until the cooldown expires. |
| **Postconditions** | A new solo selection is displayed and supporting follow-up actions are available. |

## UC10: Lock and respin dishes

| Part | Content |
|---|---|
| **Name** | Lock and respin dishes |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: keep appealing results while replacing unwanted ones. MealSlot: preserve explicit choices across spins. |
| **Preconditions** | A solo spin has produced one or more dishes. |
| **Trigger** | Diner wants to retain part of the selection and explore alternatives for the rest. |
| **Main success scenario** | 1. Diner marks desired dishes to be retained. 2. System records each retained dish in its slot. 3. Diner requests another spin. 4. System preserves the retained dishes. 5. System selects replacements for the remaining slots. 6. System displays the combined retained and replacement selection. |
| **Extensions** | 1a: Diner removes a lock → that slot becomes eligible for replacement. 1b: A slot has no current dish → system does not allow it to be locked. 4a: A previously locked dish no longer occupies its slot → system clears that stale lock. 5a: All slots are locked → the selection remains unchanged. |
| **Postconditions** | Locked dishes remain in place and unlocked slots contain the latest available results. |

## UC11: Save suggested meal

| Part | Content |
|---|---|
| **Name** | Save suggested meal |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: retain an appealing dish for later. MealSlot: keep saved state consistent across the current interface and diner profile. |
| **Preconditions** | Diner is signed in; a spin has produced a dish. |
| **Trigger** | Diner chooses to save a displayed dish. |
| **Main success scenario** | 1. Diner marks a suggested dish as saved. 2. System immediately marks the dish as saved in the current experience. 3. System adds the dish identifier to the diner’s saved-meal collection. 4. System synchronizes the updated collection to the diner profile. |
| **Extensions** | 1a: Diner selects an already-saved dish → system unsaves it instead. 3a: Diner is a guest → system can retain the selection locally but does not persist it to an authenticated profile. 4a: Profile persistence fails → system logs the failure while the optimistic local state may remain visible. |
| **Postconditions** | The diner’s saved-meal state reflects the requested change locally and, on success, in the persistent profile. |

## UC12: Browse saved meals

| Part | Content |
|---|---|
| **Name** | Browse saved meals |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: revisit previously saved ideas. MealSlot: resolve saved identifiers into current catalog information. |
| **Preconditions** | Diner is signed in and has a MealSlot profile. |
| **Trigger** | Diner opens the saved-meals area. |
| **Main success scenario** | 1. System loads the diner’s saved-meal identifiers. 2. System resolves them against the current dish catalog. 3. System displays the saved dishes. 4. Diner selects a category of interest. 5. System displays saved dishes in that category. |
| **Extensions** | 1a: Diner is not signed in → system explains that sign-in is required and offers authentication. 2a: A saved identifier no longer exists in the catalog → system omits that entry. 2b: Dish catalog loading fails → system cannot resolve saved dishes. 3a: Diner has no saved meals → system displays an empty-state message. 5a: No saved meal matches the category → system displays an empty filtered result. |
| **Postconditions** | Diner has viewed the current saved-meal collection or a category-filtered subset. |

## UC13: Remove saved meal

| Part | Content |
|---|---|
| **Name** | Remove saved meal |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: prune ideas no longer wanted. MealSlot: keep displayed and persisted saved collections consistent. |
| **Preconditions** | Diner is signed in; the saved-meals area contains the target dish. |
| **Trigger** | Diner chooses to remove a saved dish. |
| **Main success scenario** | 1. Diner requests removal of a saved dish. 2. System removes the dish from the displayed collection. 3. System stores the shortened saved-meal collection in the diner profile. 4. System reloads the profile and shows the resulting collection. |
| **Extensions** | 3a: Persistence fails → system logs the failure and may restore the server’s prior collection during refresh. 4a: Profile refresh fails → the optimistic removal remains visible until a later refresh. |
| **Postconditions** | On success, the dish is absent from the diner’s persistent and displayed saved-meal collection. |

## UC14: Watch cooking videos

| Part | Content |
|---|---|
| **Name** | Watch cooking videos |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: learn how to prepare a selected dish. Video provider: serve relevant cooking content. MealSlot: connect selections to useful follow-up guidance. |
| **Preconditions** | A solo spin has produced at least one dish and video suggestions have been prepared. |
| **Trigger** | Diner chooses the cook-at-home path. |
| **Main success scenario** | 1. System groups cooking-video suggestions by selected dish. 2. Diner reviews the suggested videos. 3. Diner selects a video. 4. System opens an embedded player for that video. 5. Diner watches the cooking content and closes the player. |
| **Extensions** | 1a: No video-service key is configured → system supplies deterministic placeholder suggestions. 1b: Video lookup fails → system supplies fallback suggestions or fewer results. 2a: No suggestions exist for a dish → system shows no video choices for that dish. 4a: External video playback is unavailable → the player cannot deliver the selected content. |
| **Postconditions** | Diner has accessed cooking guidance associated with a selected meal. |

## UC15: Find nearby place to eat

| Part | Content |
|---|---|
| **Name** | Find nearby place to eat |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: find a restaurant matching selected dishes. Venue provider: return relevant local businesses. MealSlot: provide useful distance, rating, price, and location information. |
| **Preconditions** | A spin has produced one or more dishes. |
| **Trigger** | Diner chooses the eat-outside path. |
| **Main success scenario** | 1. Diner permits MealSlot to use the current location. 2. System searches for venues related to the selected dishes. 3. System calculates distance from the diner to each result. 4. System displays venue names, cuisines, prices, ratings, addresses, and distances. 5. System plots available venue locations relative to the diner. 6. Diner opens a venue’s website for further action. |
| **Extensions** | 1a: Diner denies location access → system searches using the configured city-level fallback. 1b: Browser cannot provide location → system uses the city-level fallback. 2a: Venue-service key is missing → system returns a service notice or no live venue results. 2b: Venue search fails for one cuisine → system continues with results from the other cuisines. 3a: Location geocoding fails → system can show venue results without calculated distance. 5a: Map key is missing or map loading fails → venue details remain available without the map. |
| **Postconditions** | Diner has a set of available venue suggestions and can pursue a chosen venue externally. |

## UC16: Create party

| Part | Content |
|---|---|
| **Name** | Create party |
| **Primary actor** | Party host |
| **Stakeholders & interests** | Host: establish a shared meal-decision session. Invitees: receive a valid room to join. MealSlot: create a unique active party and identify its host. |
| **Preconditions** | Host is in party mode and has supplied a nickname. |
| **Trigger** | Host requests a new party. |
| **Main success scenario** | 1. System validates the host nickname. 2. System creates an active party with a six-character code. 3. System adds the creator as the first party member and host. 4. System initializes the host’s party preferences. 5. System displays the active party code and collaborative experience. 6. System establishes live presence for the host. |
| **Extensions** | 1a: Nickname is empty or invalid → system prevents party creation. 2a: Generated code collides with an existing party → system retries or reports creation failure. 2b: Party storage fails → system reports that the party could not be created. 4a: Host has saved account allergens → system initializes party allergens from that profile. 6a: Cross-device realtime is not configured → system uses same-origin browser communication only. |
| **Postconditions** | An active party exists with a unique code, and the creator is its host member. |

## UC17: Share party code

| Part | Content |
|---|---|
| **Name** | Share party code |
| **Primary actor** | Party host |
| **Stakeholders & interests** | Host: invite others quickly. Invitee: receive the correct join code. MealSlot: preserve room identity during invitation. |
| **Preconditions** | Host has created an active party and its code is visible. |
| **Trigger** | Host decides to invite another diner. |
| **Main success scenario** | 1. Host requests a copy of the party code. 2. System places the six-character code on the clipboard. 3. System confirms that the code was copied. 4. Host sends the code to an invitee through an external communication channel. |
| **Extensions** | 2a: Clipboard access is unavailable → host manually copies the displayed code. 4a: Host sends an incorrect or incomplete code → invitee cannot join and requests the correct code. |
| **Postconditions** | Invitee possesses the party code needed to attempt joining. |

## UC18: Join party

| Part | Content |
|---|---|
| **Name** | Join party |
| **Primary actor** | Party member |
| **Stakeholders & interests** | Member: enter the intended shared decision session. Host: see the correct participant arrive. MealSlot: validate membership and synchronize party state. |
| **Preconditions** | An active party exists; prospective member has its six-character code and a nickname. |
| **Trigger** | Prospective member requests to join the party. |
| **Main success scenario** | 1. Member supplies the party code and nickname. 2. System validates the join information. 3. System locates the active party. 4. System adds the diner as a party member. 5. System loads current members, preferences, selections, locks, votes, and recent state. 6. System establishes live presence and displays the collaborative experience. |
| **Extensions** | 1a: Nickname is empty → system prevents the join request. 1b: Code is not six valid characters → system rejects the request. 3a: Party does not exist or is inactive → system reports that the party was not found. 4a: Membership storage fails → system reports that joining failed. 6a: WebSocket transport is unavailable or unconfigured → system uses same-origin browser communication, limiting cross-device synchronization. |
| **Postconditions** | Diner is a member of the requested active party and can participate in its shared state. |

## UC19: Set party preferences

| Part | Content |
|---|---|
| **Name** | Set party preferences |
| **Primary actor** | Party participant |
| **Stakeholders & interests** | Participant: have dietary needs represented. Other participants: receive a group result safe for everyone. Host: spin using the merged constraints. MealSlot: combine preferences predictably. |
| **Preconditions** | Participant has joined an active party. |
| **Trigger** | Participant decides to state or change dietary needs. |
| **Main success scenario** | 1. System shows the participant’s current diet and allergen selections. 2. Participant selects a diet. 3. Participant selects allergens to exclude. 4. System stores the participant’s preferences. 5. System merges all members’ preferences into party constraints. 6. System shares the updated party state with the active session. |
| **Extensions** | 1a: Participant has saved profile allergens → system initializes the member preferences with those allergens. 2a: Participant selects a different diet → system replaces the previous diet selection. 3a: Participant removes an allergen → system removes it from that member’s preferences and recomputes the group union. 4a: Preference update fails → prior server preferences and merged constraints remain authoritative. 5a: Combined vegan and allergen restrictions are excessively strict → system flags a conflict and can suggest relaxing a constraint. |
| **Postconditions** | Participant preferences and the party’s merged constraints reflect the latest successful update. |

## UC20: Reach party meal decision

| Part | Content |
|---|---|
| **Name** | Reach party meal decision |
| **Primary actor** | Party host |
| **Stakeholders & interests** | Host: guide the group to a final selection. Party members: see synchronized choices, express preferences, and discuss results. MealSlot: enforce host authority, group constraints, vote rules, and live synchronization. |
| **Preconditions** | Host and at least one participant are present in an active party; current party preferences are available. |
| **Trigger** | Host starts a group meal decision. |
| **Main success scenario** | 1. Host chooses the three meal categories and desired meal priorities. 2. Host requests a group spin. 3. System applies merged party constraints and produces a synchronized three-dish selection. 4. Party members review the shared dishes and cast keep or reroll votes. 5. System totals the votes and applies the group’s quorum decisions. 6. Host continues the decision process while preserving accepted dishes. 7. Participants exchange messages about the shared choices. 8. Group accepts a final selection. 9. System retains recent spin summaries for the session. |
| **Extensions** | 1a: A non-host attempts to change authoritative spin state → system prevents the action. 2a: Host is not an active member → system requires joining first. 2b: Group spin fails → system reports the failure; the party spin service may return placeholder selections when its internal solo spin is unavailable. 3a: Live transport is interrupted → participants may not receive synchronized results until communication resumes. 4a: Member changes a vote → system removes that member’s prior vote for the slot. 5a: Keep votes reach quorum → system locks that slot. 5b: Reroll votes reach quorum → host rerolls that slot. 5c: Neither vote reaches quorum → slot remains unchanged. 6a: Host changes one slot’s category → system rerolls that slot while preserving the others. 7a: Participant submits an empty message → system ignores it. 7b: Participant leaves → system removes that membership and presence; the party remains active. 7c: Host leaves → stored room remains active and remaining participants continue with the available state. |
| **Postconditions** | Party has a synchronized final meal selection, with recent decision history retained for the active session. |


