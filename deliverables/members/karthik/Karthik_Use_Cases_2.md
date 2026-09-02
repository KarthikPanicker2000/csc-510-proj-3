# MealSlot: 20 Main Use Cases

## UC1 — Create Account

| Part | Content |
|---|---|
| **Name** | Create Account |
| **Primary actor** | Guest diner |
| **Stakeholders & interests** | Guest diner: obtain a personal MealSlot account. Authentication provider: establish a secure identity. MealSlot: associate preferences and saved meals with a stable user. |
| **Preconditions** | The guest is not signed in, and the authentication service is available. |
| **Trigger** | The guest decides to register for MealSlot. |
| **Main success scenario** | 1. Guest begins account registration.<br>2. MealSlot presents the supported registration method.<br>3. Guest supplies valid identity information.<br>4. Authentication provider verifies the information and creates an identity.<br>5. MealSlot creates the corresponding diner profile.<br>6. MealSlot signs in the diner and opens the account area. |
| **Extensions** | **3a.** Submitted identity information is invalid → authentication provider requests corrected information.<br>**3b.** The identity is already registered → MealSlot directs the guest to sign in.<br>**4a.** Authentication provider is unavailable → registration remains incomplete and the guest remains signed out.<br>**5a.** MealSlot profile creation fails → the identity exists, but MealSlot reports or records the profile synchronization failure. |
| **Postconditions** | A protected authentication identity and corresponding MealSlot profile exist, and the diner is signed in. |

## UC2 — Sign In

| Part | Content |
|---|---|
| **Name** | Sign In |
| **Primary actor** | Registered diner |
| **Stakeholders & interests** | Diner: regain access to saved meals and preferences. MealSlot: associate activity with the correct profile. Authentication provider: verify identity securely. |
| **Preconditions** | The diner has a registered identity and is currently signed out. |
| **Trigger** | The diner requests access to their MealSlot account. |
| **Main success scenario** | 1. Diner begins the sign-in process.<br>2. MealSlot transfers authentication responsibility to the authentication provider.<br>3. Diner supplies valid credentials.<br>4. Authentication provider verifies the diner and establishes a session.<br>5. MealSlot retrieves or establishes the corresponding diner profile.<br>6. MealSlot displays the signed-in experience with the diner’s stored information. |
| **Extensions** | **3a.** Credentials are rejected → the diner remains signed out and may retry.<br>**4a.** Authentication provider is unavailable → no MealSlot session is established.<br>**5a.** No corresponding MealSlot profile exists → MealSlot attempts to create the missing profile.<br>**5b.** Profile retrieval fails → authentication may succeed while personalized MealSlot information remains unavailable. |
| **Postconditions** | The diner has an authenticated session and MealSlot has loaded the associated profile. |

## UC3 — Sign Out

| Part | Content |
|---|---|
| **Name** | Sign Out |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: end access to the account on the current browser. MealSlot: prevent subsequent activity from being attributed to the previous diner. |
| **Preconditions** | The diner has an active authenticated session. |
| **Trigger** | The diner requests to sign out. |
| **Main success scenario** | 1. Diner requests to end the current session.<br>2. MealSlot submits the sign-out request to the authentication provider.<br>3. Authentication provider invalidates the session.<br>4. MealSlot clears the active diner information from the current experience.<br>5. MealSlot returns the diner to a signed-out page. |
| **Extensions** | **2a.** Authentication provider cannot process the request → the authenticated session may remain active.<br>**3a.** Session has already expired → MealSlot proceeds to the signed-out experience.<br>**4a.** Another browser tab retains stale account information → that tab continues displaying stale data until its session state is refreshed. |
| **Postconditions** | The current authenticated session has ended and protected account features require another sign-in. |
| **Implementation discrepancy** | MealSlot contains both provider-based sign-out behavior and local state-clearing behavior. Runtime verification is needed to confirm the result from every sign-out entry point. |

## UC4 — Update Display Name

| Part | Content |
|---|---|
| **Name** | Update Display Name |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: maintain an accurate account identity. MealSlot: display a consistent name throughout the application. Authentication provider: retain the account’s primary profile information. |
| **Preconditions** | The diner is signed in and can access account settings. |
| **Trigger** | The diner decides to change the account display name. |
| **Main success scenario** | 1. Diner opens account settings.<br>2. MealSlot presents the current account information.<br>3. Diner supplies a new display name.<br>4. Authentication provider stores the new name.<br>5. MealSlot detects the updated identity information.<br>6. MealSlot synchronizes its diner profile and displays the new name. |
| **Extensions** | **3a.** The new name is rejected by the authentication provider → the existing name remains unchanged.<br>**4a.** The diner submits the existing name → MealSlot performs no profile update.<br>**5a.** Identity synchronization is delayed → MealSlot continues showing the previous name until a later refresh.<br>**6a.** MealSlot profile synchronization fails → the authentication profile and MealSlot profile temporarily contain different names. |
| **Postconditions** | The updated display name is stored and shown by MealSlot after successful synchronization. |

## UC5 — Manage Allergen Preferences

| Part | Content |
|---|---|
| **Name** | Manage Allergen Preferences |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: avoid unsuitable meal suggestions. MealSlot: retain reliable dietary information for future spins. |
| **Preconditions** | The diner is signed in and the allergen catalog is available. |
| **Trigger** | The diner opens dietary preferences. |
| **Main success scenario** | 1. Diner opens the dietary-preference section.<br>2. MealSlot loads the supported allergens and the diner’s stored selections.<br>3. Diner reviews the current selections.<br>4. Diner adds or removes allergen selections.<br>5. Diner saves the revised preferences.<br>6. MealSlot stores the preferences and updates the active diner profile. |
| **Extensions** | **2a.** The allergen catalog cannot be loaded → MealSlot cannot present a complete selection list.<br>**2b.** A previously stored allergen is absent from the current catalog → MealSlot omits that value from the selectable preferences.<br>**5a.** The diner leaves without saving → the previously stored preferences remain authoritative.<br>**6a.** Saving fails → MealSlot reports the failure and retains the previously stored preferences. |
| **Postconditions** | The successfully saved allergen selections are associated with the diner’s MealSlot profile. |

## UC6 — Personalize Meal Suggestions

| Part | Content |
|---|---|
| **Name** | Personalize Meal Suggestions |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: receive meals that reflect the current occasion, dietary constraints, and priorities. MealSlot: construct a valid set of inputs for meal selection. |
| **Preconditions** | The MealSlot meal-selection page is available. |
| **Trigger** | The diner prepares a personalized meal spin. |
| **Main success scenario** | 1. Diner selects meal categories for the available slots.<br>2. MealSlot records the selected categories.<br>3. Diner selects relevant dietary tags and allergen exclusions.<br>4. Diner selects meal priorities such as healthier, cheaper, or faster choices.<br>5. MealSlot combines the categories, constraints, and priorities into the active spin configuration.<br>6. MealSlot presents the completed configuration for the next spin. |
| **Extensions** | **1a.** Diner selects a preset → MealSlot applies the preset’s category combination.<br>**3a.** A signed-in diner has stored allergens → MealSlot incorporates the saved selections into the available configuration.<br>**3b.** Selected restrictions eliminate the available dishes → the subsequent spin produces unresolved meal positions.<br>**4a.** Several priorities are activated → MealSlot combines their scoring effects rather than treating them as strict filters. |
| **Postconditions** | A session-level configuration is ready to guide the next meal spin. |

## UC7 — Spin for Meals

| Part | Content |
|---|---|
| **Name** | Spin for Meals |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: receive concrete meal suggestions. MealSlot: provide varied suggestions that respect the current configuration. |
| **Preconditions** | Three meal categories have been selected and MealSlot can access its dish catalog. |
| **Trigger** | The diner starts a meal spin. |
| **Main success scenario** | 1. Diner submits the active meal configuration.<br>2. MealSlot retrieves dishes matching the selected categories and constraints.<br>3. MealSlot scores the eligible dishes using the active priorities.<br>4. MealSlot selects distinct dishes for the available positions.<br>5. MealSlot presents the selected dishes to the diner.<br>6. MealSlot temporarily pauses additional spins and retrieves related dining information. |
| **Extensions** | **1a.** Required categories are missing → MealSlot rejects the spin request.<br>**2a.** A category has no eligible dish → MealSlot places an unresolved suggestion in that position.<br>**4a.** Too few distinct eligible dishes exist → MealSlot returns the available unique dishes and unresolved remaining positions.<br>**6a.** Diner immediately requests another spin → MealSlot delays the request until the cooldown ends. |
| **Postconditions** | A set of meal suggestions or explicit unresolved positions is displayed. |
| **Implementation discrepancy** | The displayed category values and seeded category values use inconsistent capitalization. With the supplied data, ordinary spins may return unresolved suggestions even though matching dishes appear to exist. |

## UC8 — Lock Meal Suggestions

| Part | Content |
|---|---|
| **Name** | Lock Meal Suggestions |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: retain appealing dishes while replacing unwanted suggestions. MealSlot: preserve valid selections during a partial reroll. |
| **Preconditions** | A completed spin is displayed. |
| **Trigger** | The diner chooses one or more suggestions to retain. |
| **Main success scenario** | 1. Diner identifies the meal suggestions to keep.<br>2. MealSlot marks those suggestions as locked.<br>3. Diner starts another spin.<br>4. MealSlot validates and preserves the locked dishes.<br>5. MealSlot selects new dishes for the unlocked positions.<br>6. MealSlot displays the combined retained and newly selected suggestions. |
| **Extensions** | **2a.** Diner unlocks a previously retained suggestion → MealSlot includes that position in the next reroll.<br>**4a.** A locked dish no longer exists in the catalog → MealSlot replaces it instead of preserving an invalid reference.<br>**4b.** A legacy lock identifies only a position rather than a dish → MealSlot does not treat it as a valid dish lock.<br>**5a.** No eligible replacement exists → MealSlot places an unresolved suggestion in the affected position. |
| **Postconditions** | Valid locked dishes remain selected and unlocked positions contain new or unresolved suggestions. |

## UC9 — Save a Meal

| Part | Content |
|---|---|
| **Name** | Save a Meal |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: retain an appealing meal for later reference. MealSlot: associate the selected dish with the correct diner or browser session. |
| **Preconditions** | MealSlot is displaying a valid dish suggestion. |
| **Trigger** | The diner requests to save the dish. |
| **Main success scenario** | 1. Diner selects a displayed meal for saving.<br>2. MealSlot marks the meal as saved in the current experience.<br>3. MealSlot associates the dish identifier with the diner’s saved collection.<br>4. MealSlot persists the revised collection.<br>5. MealSlot updates the displayed saved status. |
| **Extensions** | **1a.** The displayed position contains no valid dish → MealSlot cannot create a saved-meal reference.<br>**3a.** Diner is signed out → MealSlot stores the selection only in the current browser’s local data.<br>**4a.** Account persistence fails → MealSlot logs the failure while the optimistic saved indicator may remain visible.<br>**4b.** Existing browser data is malformed → MealSlot cannot reliably restore the local saved collection. |
| **Postconditions** | The meal is stored in the account collection or local browser data. |
| **Implementation discrepancy** | A guest can save dishes locally, but the saved-meals page requires authentication and does not present that guest collection. Failed account persistence also does not reliably reverse the optimistic saved indicator. |

## UC10 — Browse Saved Meals

| Part | Content |
|---|---|
| **Name** | Browse Saved Meals |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: review previously saved choices. MealSlot: resolve stored dish references into useful meal information. |
| **Preconditions** | The diner is signed in and has access to the saved-meals area. |
| **Trigger** | The diner opens the saved-meals collection. |
| **Main success scenario** | 1. Diner requests the saved-meals collection.<br>2. MealSlot loads the diner’s saved dish identifiers.<br>3. MealSlot retrieves the corresponding dish information.<br>4. MealSlot displays the resolved saved meals.<br>5. Diner selects a meal category for review.<br>6. MealSlot displays saved meals belonging to that category. |
| **Extensions** | **1a.** Diner is signed out → MealSlot requests authentication instead of displaying an account collection.<br>**3a.** A saved identifier no longer refers to a known dish → MealSlot omits that stale entry.<br>**3b.** The dish catalog cannot be loaded → saved identifiers cannot be converted into full meal information.<br>**4a.** The collection is empty → MealSlot presents an empty saved-meals state. |
| **Postconditions** | The diner has reviewed the available saved meals without modifying the collection. |

## UC11 — Remove a Saved Meal

| Part | Content |
|---|---|
| **Name** | Remove a Saved Meal |
| **Primary actor** | Signed-in diner |
| **Stakeholders & interests** | Diner: keep the saved-meals collection relevant. MealSlot: persist the diner’s revised collection accurately. |
| **Preconditions** | The diner is signed in and a saved dish is displayed. |
| **Trigger** | The diner requests removal of a saved meal. |
| **Main success scenario** | 1. Diner selects a saved meal for removal.<br>2. MealSlot removes the meal from the displayed collection.<br>3. MealSlot submits the revised saved-meal collection for persistence.<br>4. MealSlot stores the revised collection.<br>5. MealSlot refreshes the diner profile.<br>6. MealSlot displays the authoritative saved-meal collection. |
| **Extensions** | **1a.** The referenced meal is already absent → the collection remains unchanged.<br>**2a.** The removed meal was the last item in the selected category → MealSlot presents an empty category result.<br>**3a.** Network communication fails → MealSlot logs the failure and the meal may reappear after profile refresh.<br>**4a.** Persistence returns an unsuccessful response → the current implementation may not recognize the rejection before refreshing. |
| **Postconditions** | A successful removal no longer appears in the diner’s persisted saved-meal collection. |
| **Implementation discrepancy** | The removal workflow does not reliably check unsuccessful persistence responses, so the temporary display may differ from the stored collection. |

## UC12 — Watch Cooking Videos

| Part | Content |
|---|---|
| **Name** | Watch Cooking Videos |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: learn how to prepare a suggested meal. Video provider: supply relevant cooking content. MealSlot: connect meal selection with actionable preparation guidance. |
| **Preconditions** | A completed meal spin contains valid dish suggestions. |
| **Trigger** | The diner requests the cook-at-home information for the suggestions. |
| **Main success scenario** | 1. MealSlot derives search terms from the selected dishes.<br>2. MealSlot requests relevant cooking videos.<br>3. Video provider returns matching results.<br>4. MealSlot groups the videos by suggested dish.<br>5. Diner reviews the available cooking videos.<br>6. Diner opens a selected video for playback. |
| **Extensions** | **2a.** Video-service credentials are unavailable → MealSlot supplies deterministic development video results.<br>**3a.** Video provider rejects or fails the request → MealSlot supplies fallback results.<br>**3b.** Results exist for only some dishes → MealSlot displays the available groups and leaves other dishes without videos.<br>**6a.** External playback is unavailable → MealSlot retains the video information but cannot play the selected content. |
| **Postconditions** | The diner can access cooking-video guidance for at least one suggested dish. |

## UC13 — Find Nearby Restaurants

| Part | Content |
|---|---|
| **Name** | Find Nearby Restaurants |
| **Primary actor** | Diner |
| **Stakeholders & interests** | Diner: find places serving food related to the selected meals. Location service: provide the diner’s position. Places provider: return relevant nearby businesses. |
| **Preconditions** | A completed meal spin contains cuisine or meal information. |
| **Trigger** | The diner requests eat-outside options. |
| **Main success scenario** | 1. Diner requests nearby dining options.<br>2. MealSlot requests the diner’s current location.<br>3. Diner grants location access.<br>4. MealSlot derives restaurant searches from the selected meals.<br>5. Places provider returns nearby matching restaurants.<br>6. MealSlot displays the restaurants with available location and distance information. |
| **Extensions** | **2a.** Browser location services are unavailable → MealSlot searches from its configured default location.<br>**3a.** Diner denies location access → MealSlot uses the configured default location and identifies that fallback.<br>**5a.** One cuisine search fails → MealSlot displays results returned by the remaining searches.<br>**6a.** Mapping configuration is unavailable → restaurant information may remain visible without an interactive map. |
| **Postconditions** | The diner receives available nearby restaurant suggestions related to the selected meals. |

## UC14 — Create a Party

| Part | Content |
|---|---|
| **Name** | Create a Party |
| **Primary actor** | Party host |
| **Stakeholders & interests** | Host: establish a shared meal-decision session. Participants: receive a code for joining. MealSlot: maintain party membership and shared constraints. |
| **Preconditions** | The party service and persistent storage are available. |
| **Trigger** | A diner decides to start a MealSlot party. |
| **Main success scenario** | 1. Host provides a party nickname.<br>2. MealSlot validates the nickname.<br>3. MealSlot creates an active party with a unique joining code.<br>4. MealSlot registers the host as the first member.<br>5. MealSlot initializes the party constraints from available host preferences.<br>6. MealSlot displays the active party and its joining code. |
| **Extensions** | **1a.** Nickname is missing or exceeds the accepted length → MealSlot does not create the party.<br>**3a.** Generated code conflicts with an existing party → creation fails because the implementation does not clearly retry with another code.<br>**4a.** Membership persistence fails → the party cannot be entered as an operational host session.<br>**5a.** Host has no saved dietary preferences → MealSlot initializes the party without account-derived allergens. |
| **Postconditions** | An active party exists, the host is a member, and a joining code is available. |
| **Implementation discrepancy** | The browser prevents a blank nickname, but direct party creation may accept a nickname containing only whitespace. |

## UC15 — Join a Party

| Part | Content |
|---|---|
| **Name** | Join a Party |
| **Primary actor** | Joining diner |
| **Stakeholders & interests** | Joining diner: participate in a shared meal decision. Host and existing members: include the new diner’s presence and preferences. |
| **Preconditions** | An active party with a valid joining code exists. |
| **Trigger** | A diner submits a party code and nickname. |
| **Main success scenario** | 1. Diner provides the joining code and a party nickname.<br>2. MealSlot validates the supplied values.<br>3. MealSlot locates the active party.<br>4. MealSlot creates a membership for the diner.<br>5. MealSlot returns the party and membership identity.<br>6. MealSlot loads the shared party state and displays the diner as a participant. |
| **Extensions** | **2a.** Code is not six characters long or nickname is invalid → MealSlot rejects the request.<br>**3a.** Code does not identify an active party → MealSlot reports that the party cannot be joined.<br>**4a.** The same diner joins repeatedly → the implementation may create multiple party memberships rather than reusing the original membership.<br>**4b.** Diner is not signed in → MealSlot creates a guest party membership without account-derived preferences. |
| **Postconditions** | A membership exists for the joining diner and the party state is available. |
| **Implementation discrepancy** | The joining service returns a membership identifier, but the party page discards it. Consequently, a joining diner cannot reliably activate member-specific realtime, preference, voting, or chat behavior. |

## UC16 — Set Party Preferences

| Part | Content |
|---|---|
| **Name** | Set Party Preferences |
| **Primary actor** | Party member |
| **Stakeholders & interests** | Party member: communicate dietary and practical constraints. Other members: receive suggestions safe and acceptable for the group. MealSlot: derive one group constraint set. |
| **Preconditions** | The diner has an active party membership identity. |
| **Trigger** | The member decides to submit party meal preferences. |
| **Main success scenario** | 1. Member opens the party preference area.<br>2. MealSlot presents the member’s current dietary, allergen, budget, and time preferences.<br>3. Member revises the preferences.<br>4. Member saves the revised preferences.<br>5. MealSlot stores the preferences with the member’s party membership.<br>6. MealSlot merges all member preferences into the party constraints.<br>7. MealSlot makes the merged constraints available for subsequent party spins. |
| **Extensions** | **3a.** Submitted preference values are outside the supported format → MealSlot rejects the update.<br>**5a.** Existing member preferences contain malformed information → MealSlot treats the malformed information as unavailable during merging.<br>**6a.** Members specify different budgets or preparation times → MealSlot uses the most restrictive supported values.<br>**6b.** Members specify different allergens → MealSlot combines the exclusions for the group. |
| **Postconditions** | The member’s preferences and the resulting merged party constraints are stored. |
| **Implementation discrepancy** | A member who joined through the current party page generally lacks the retained membership identity required to submit these preferences. |

## UC17 — Spin for the Party

| Part | Content |
|---|---|
| **Name** | Spin for the Party |
| **Primary actor** | Party host |
| **Stakeholders & interests** | Host: generate shared meal choices. Members: receive suggestions reflecting group constraints. MealSlot: synchronize one authoritative party result. |
| **Preconditions** | An active party exists, the host has an active membership identity, and party constraints are available. |
| **Trigger** | The host starts a group meal spin. |
| **Main success scenario** | 1. Host selects the party’s meal categories and priorities.<br>2. Host starts the group spin.<br>3. MealSlot combines the host’s selections with the merged party constraints.<br>4. MealSlot preserves the party’s retained meal positions.<br>5. MealSlot selects distinct dishes for the remaining positions.<br>6. MealSlot displays the result to the host.<br>7. MealSlot broadcasts the result to connected party members. |
| **Extensions** | **2a.** A non-host member attempts to start the spin → MealSlot denies the group-spin operation.<br>**3a.** Party state cannot be retrieved → MealSlot cannot apply the group constraints.<br>**5a.** The normal meal-selection operation fails → MealSlot substitutes its predefined party fallback suggestions.<br>**5b.** Eligible distinct dishes cannot fill every position → MealSlot inserts unresolved party suggestions. |
| **Postconditions** | The party has a new authoritative meal result ready for group review. |
| **Implementation discrepancy** | The predefined fallback dishes are not filtered against the party’s merged allergen constraints. The browser’s realtime protocol also differs from the supplied realtime server protocol, so other browsers may not receive the result. |

## UC18 — Vote on Party Meals

| Part | Content |
|---|---|
| **Name** | Vote on Party Meals |
| **Primary actor** | Party member |
| **Stakeholders & interests** | Party member: express approval or rejection of each result. Host: understand group preference. MealSlot: translate group votes into retained or rerolled positions. |
| **Preconditions** | A party spin result is displayed and the diner has an active party membership identity. |
| **Trigger** | The member evaluates a party meal suggestion. |
| **Main success scenario** | 1. Member selects a disposition for a meal position.<br>2. MealSlot records the member’s vote for that position.<br>3. MealSlot associates the vote with the current member and result.<br>4. MealSlot distributes the updated vote state to connected members.<br>5. MealSlot calculates the result using the active-member quorum.<br>6. MealSlot retains or releases the position according to the group decision.<br>7. MealSlot displays the updated vote totals and meal state. |
| **Extensions** | **2a.** Member changes an existing vote → MealSlot replaces the previous vote instead of counting both.<br>**3a.** Member has no recognized party membership → MealSlot cannot associate or transmit the vote.<br>**5a.** A member disconnects → MealSlot recalculates the quorum from the remaining active presence state.<br>**5b.** Votes do not reach the required quorum → the affected position remains undecided. |
| **Postconditions** | The member’s latest vote is represented in the current party decision state. |
| **Implementation discrepancy** | Joined diners generally lack a retained membership identifier, and the realtime client is incompatible with the supplied server. Reliable multi-user voting is therefore not operational in the inspected implementation. |

## UC19 — Chat with Party Members

| Part | Content |
|---|---|
| **Name** | Chat with Party Members |
| **Primary actor** | Party member |
| **Stakeholders & interests** | Party members: discuss suggestions during the decision process. MealSlot: deliver messages to the correct active party. |
| **Preconditions** | The diner has an active party membership and a functioning party communication channel. |
| **Trigger** | The member submits a party message. |
| **Main success scenario** | 1. Member composes a nonempty party message.<br>2. MealSlot associates the message with the member and active party.<br>3. MealSlot adds the message to the sender’s conversation.<br>4. MealSlot transmits the message to connected party members.<br>5. Receiving MealSlot sessions display the sender, message, and time.<br>6. Party members continue the conversation through additional messages. |
| **Extensions** | **1a.** Message contains only whitespace → MealSlot does not send it.<br>**3a.** A message with an already processed identity is received → MealSlot suppresses the duplicate.<br>**4a.** External realtime configuration is absent → communication is limited to compatible same-origin browser contexts.<br>**5a.** A member reloads the party → previous chat history is lost because the conversation is not persisted as party history. |
| **Postconditions** | Connected party members can see the newly delivered message during the active session. |
| **Implementation discrepancy** | The browser sends raw WebSocket-style messages, while the supplied realtime server uses Socket.IO events. Cross-browser chat therefore fails in the inspected configuration, even though the sender may see a local copy. |

## UC20 — Leave a Party

| Part | Content |
|---|---|
| **Name** | Leave a Party |
| **Primary actor** | Party member |
| **Stakeholders & interests** | Departing member: exit the shared session. Remaining members: maintain accurate membership and quorum information. MealSlot: remove obsolete membership and presence state. |
| **Preconditions** | The diner belongs to an active party. |
| **Trigger** | The member requests to leave the party. |
| **Main success scenario** | 1. Member requests to leave the active party.<br>2. MealSlot identifies the member’s party membership.<br>3. MealSlot removes the membership from the party.<br>4. MealSlot communicates the departure to remaining connected members.<br>5. MealSlot clears the departing member’s local party state.<br>6. MealSlot returns the diner to the party entry page.<br>7. Remaining members continue with the revised membership state. |
| **Extensions** | **2a.** Membership identity is unavailable → MealSlot cannot remove the authoritative membership.<br>**3a.** Membership was already removed → the removal operation reports that no membership exists.<br>**3b.** Persistent removal fails → the diner may leave locally while remaining in the stored party membership list.<br>**4a.** Departing member was treated as host → the remaining live-member ordering determines who receives host behavior. |
| **Postconditions** | The member no longer participates in the party, and remaining members operate with the revised membership state. |
| **Implementation discrepancy** | The current party page clears local state and reloads without invoking the implemented membership-removal operation. The stored party membership can therefore remain after the diner appears to leave. |

