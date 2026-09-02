# Deliverable D2: Reverse-Engineered Use Cases (MealSlot)

This document contains 20 comprehensive use cases reverse-engineered from the **MealSlot** (`fixmeseb/mealslots`) codebase. Each use case strictly adheres to the structural and content guidelines defined in `usecases0.md`: clean main success scenarios with no branch logic, "what, not how" domain specifications (no UI widget or database talk), and rich multi-branch extensions detailing variation and error flows.

---

## UC1: Spin Single Meal

| Part | Content |
|---|---|
| **Name** | Spin single meal |
| **Primary actor** | Hungry User |
| **Stakeholders & interests** | User (wants a quick, randomized meal recommendation matching basic category preferences); System (maintains engagement and avoids repetitive recommendations). |
| **Preconditions** | System is accessible; dish catalog is available. |
| **Trigger** | User requests a single meal recommendation. |
| **Main success scenario** | 1. User selects a meal category (e.g., Dinner, Dessert).<br>2. User initiates the meal spin.<br>3. System evaluates candidate dishes in the selected category against active preference filters.<br>4. System selects a matching dish using randomized selection.<br>5. System presents the chosen meal recommendation along with cooking and dining options. |
| **Extensions** | **3a. No dishes match category and active filters:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user that active constraints yielded no matches.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System offers fallback recommendation from unconstrained catalog.<br>**3b. Network connection fails during request:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user of connection timeout.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System prompts user to retry.<br>**4a. User rapidly repeats spin requests:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System throttles excessive requests and displays retry delay message. |
| **Postconditions** | Single meal recommendation is displayed with options to view recipes or nearby venues. |

---

## UC2: Plan Full-Day Meals

| Part | Content |
|---|---|
| **Name** | Plan full-day meals |
| **Primary actor** | Meal Planner |
| **Stakeholders & interests** | User (wants a complete, coordinated multi-meal itinerary for breakfast, lunch, dinner, and dessert without manual picking). |
| **Preconditions** | User is on the meal planning view. |
| **Trigger** | User initiates a full-day meal plan spin. |
| **Main success scenario** | 1. User selects multi-meal day planning mode.<br>2. User initiates full-day plan generation.<br>3. System retrieves candidates across all four standard categories (Breakfast, Lunch, Dinner, Dessert).<br>4. System applies active dietary rules across all categories simultaneously.<br>5. System selects one dish for each meal slot and estimates combined preparation time and nutritional totals.<br>6. System displays the complete daily meal itinerary. |
| **Extensions** | **3a. Candidate pool for one specific category is empty:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user which specific meal category lacked matches.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System fills remaining categories and applies default candidates to the empty category.<br>**4a. Combined dietary rules eliminate all candidates across multiple categories:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System warns user of overly restrictive multi-category constraints.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System suggests relaxing specific constraints.<br>**5a. User rejects a single slot in the generated plan:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 User requests a respin of only that specific meal slot.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System replaces only the targeted slot while keeping the other three meals intact. |
| **Postconditions** | Synchronized 4-meal daily itinerary is generated and displayed. |

---

## UC3: Filter Dietary & Allergen Constraints

| Part | Content |
|---|---|
| **Name** | Apply dietary and allergen filters |
| **Primary actor** | Health-Conscious Diner |
| **Stakeholders & interests** | Diner (wants strict safety guarantees that allergens like peanuts, gluten, or dairy are excluded); System (prevents hazardous food suggestions). |
| **Preconditions** | Filter configuration interface is open. |
| **Trigger** | Diner modifies allergen exclusions or dietary tags (e.g., Vegan, Halal, Gluten-Free). |
| **Main success scenario** | 1. Diner selects allergen exclusions and dietary preferences.<br>2. Diner confirms the updated filter preferences.<br>3. System validates the selected combination of dietary rules.<br>4. System updates active preference criteria.<br>5. System updates available dish catalog to exclude all non-compliant meals.<br>6. System confirms active filter criteria to the diner. |
| **Extensions** | **3a. Diner selects mutually exclusive constraints (e.g., strict Vegan and Carnivore):**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System warns diner that combination produces an empty candidate selection.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System highlights conflicting options and prompts diner to adjust selections.<br>**4a. Diner clears all active filters:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System resets preference state to default unconstrained catalog. |
| **Postconditions** | All subsequent meal generation strictly excludes dishes violating selected dietary rules. |

---

## UC4: View Cooking Recipe & Tutorial

| Part | Content |
|---|---|
| **Name** | View cooking recipe and tutorial |
| **Primary actor** | Home Cook |
| **Stakeholders & interests** | Home Cook (wants clear preparation instructions, ingredient checklists, and video walkthroughs); Content Providers (want accurate video attribution). |
| **Preconditions** | A meal recommendation has been selected. |
| **Trigger** | Home Cook requests recipe instructions for the current dish. |
| **Main success scenario** | 1. Home Cook requests recipe details for the chosen meal.<br>2. System retrieves structured recipe instructions including ingredient quantities, prep time, and step-by-step directions.<br>3. System retrieves matching video cooking tutorials for the dish title.<br>4. System displays recipe instructions alongside embedded video player. |
| **Extensions** | **2a. Recipe generation service is temporarily unreachable:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System presents cached fallback recipe instructions for the dish category.<br>**3a. Video tutorial service quota is exceeded or video is unavailable:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays fallback direct web search link for the recipe video.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System continues displaying full text recipe steps and ingredients.<br>**4a. Home Cook marks ingredients as gathered:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System updates interactive checklist state for the session. |
| **Postconditions** | Recipe instructions, ingredient list, and video tutorial are presented. |

---

## UC5: Locate Nearby Dining Venues

| Part | Content |
|---|---|
| **Name** | Locate nearby dining venues |
| **Primary actor** | Restaurant Diner |
| **Stakeholders & interests** | Diner (wants to find open local restaurants serving the chosen cuisine); Local Restaurants (want customer discovery). |
| **Preconditions** | A meal recommendation is selected. |
| **Trigger** | Diner requests local restaurant options for the current dish. |
| **Main success scenario** | 1. Diner requests nearby dining options.<br>2. System obtains diner's geographic coordinates.<br>3. System searches for nearby restaurants serving the selected dish or cuisine type.<br>4. System calculates distance and travel orientation to candidate venues.<br>5. System displays interactive map markers and venue summary cards with ratings and addresses. |
| **Extensions** | **2a. Geographic location permission is denied by diner:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System prompts diner to enter a city name or postal code manually.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System proceeds with location search using entered postal region.<br>**3a. No restaurants found within standard search radius:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System expands search radius and retries query.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 If still no venues found, system notifies diner and suggests broader cuisine keywords.<br>**4a. Map rendering service encounters asynchronous script loading latency:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays venue list view with addresses and ratings while map canvas finishes loading. |
| **Postconditions** | Nearby restaurant options are displayed with addresses, distances, and map positions. |

---

## UC6: Create Group Party Room

| Part | Content |
|---|---|
| **Name** | Create group party room |
| **Primary actor** | Party Host |
| **Stakeholders & interests** | Host (wants to organize group dining decisions); Group Members (want to participate in collective voting). |
| **Preconditions** | System is accessible. |
| **Trigger** | Host requests to create a new group party. |
| **Main success scenario** | 1. Host enters a party title and optional nickname.<br>2. Host confirms party creation.<br>3. System creates a new party session with a unique 6-character room code.<br>4. System establishes a real-time communication channel for the room.<br>5. System assigns host administrative privileges to the creator.<br>6. System transitions host into the active party room interface. |
| **Extensions** | **1a. Host leaves party title blank:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System assigns an automated friendly party name (e.g., "Dinner Party").<br>**3a. System storage or session service is unreachable:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts host of service unavailability.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System prompts host to retry creation after a brief interval.<br>**4a. Real-time communication channel fails to initialize:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System switches to polling fallback and alerts host of degraded real-time sync. |
| **Postconditions** | A new party room is active with real-time connectivity and a shareable join code. |

---

## UC7: Join Existing Party Room

| Part | Content |
|---|---|
| **Name** | Join existing party room |
| **Primary actor** | Party Guest |
| **Stakeholders & interests** | Guest (wants to enter friend's party session); Host & Group (want all members connected to one room). |
| **Preconditions** | An active party room exists. |
| **Trigger** | Guest submits a 6-character party room code or opens an invitation link. |
| **Main success scenario** | 1. Guest provides the party room code and a display nickname.<br>2. System validates that the party room code exists and is currently active.<br>3. System adds guest to the party member roster.<br>4. System connects guest to the room's real-time communication channel.<br>5. System synchronizes current room state, preferences, and chat history to the guest.<br>6. System broadcasts member joined notification to all existing participants. |
| **Extensions** | **2a. Party code is invalid or does not exist:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays error notification indicating invalid party code.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System prompts guest to re-enter code.<br>**2b. Party session has ended or expired:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts guest that the party has concluded.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System directs guest back to the main homepage.<br>**3a. Guest nickname is already taken in the room:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System automatically appends a numeric suffix (e.g., "Alex (2)") and completes joining. |
| **Postconditions** | Guest is connected to the party room, visible in the roster, and synchronized to events. |

---

## UC8: Synchronize Group Party Spin

| Part | Content |
|---|---|
| **Name** | Synchronize group party spin |
| **Primary actor** | Party Host |
| **Stakeholders & interests** | All Party Members (want an equitable, synchronized group meal decision that respects everyone's restrictions). |
| **Preconditions** | Host and members are connected inside an active party room. |
| **Trigger** | Host initiates a group meal spin. |
| **Main success scenario** | 1. Host triggers group spin.<br>2. System aggregates and merges dietary restrictions across all connected party members.<br>3. System filters candidate dishes against the merged group restriction set.<br>4. System selects a randomized winning dish.<br>5. System broadcasts simultaneous spin animation event to all connected member devices.<br>6. System displays the synchronized winning meal result across all member screens simultaneously. |
| **Extensions** | **2a. Merged group restrictions eliminate all possible dishes in catalog:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System notifies party that combined restrictions allow zero dishes.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System highlights conflicting restrictions and prompts members to relax constraints.<br>**5a. Member device experiences temporary network latency during spin:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System catches member up to the resolved outcome immediately upon reconnection.<br>**1a. Non-host participant attempts to trigger group spin:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System rejects action and informs participant that only the host may initiate group spins. |
| **Postconditions** | All party participants view the identical synchronized meal spin outcome. |

---

## UC9: Exchange Realtime Party Messages

| Part | Content |
|---|---|
| **Name** | Exchange realtime party messages |
| **Primary actor** | Party Participant |
| **Stakeholders & interests** | All Room Members (want instant text communication to discuss food options). |
| **Preconditions** | Participant is connected to active party room. |
| **Trigger** | Participant sends a chat message. |
| **Main success scenario** | 1. Participant enters text message into party chat.<br>2. Participant sends message.<br>3. System validates message payload and attaches sender nickname and timestamp.<br>4. System broadcasts message across real-time channel to all room participants.<br>5. System appends message to chat streams across all member screens. |
| **Extensions** | **1a. Participant submits empty or whitespace-only message:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System ignores submission and keeps input field focused.<br>**3a. Real-time connection drops during message transmission:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System queues message locally.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System attempts connection recovery and sends queued message upon reconnection.<br>**4a. Message text exceeds maximum length threshold:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System truncates message or prompts user to shorten text. |
| **Postconditions** | Message is delivered and rendered chronologically across all participant chat windows. |

---

## UC10: Authenticate User Account

| Part | Content |
|---|---|
| **Name** | Authenticate user account |
| **Primary actor** | Registered User |
| **Stakeholders & interests** | User (wants secure access to saved preferences and favorites); System (maintains user session integrity). |
| **Preconditions** | User is on authentication screen. |
| **Trigger** | User submits login or registration credentials. |
| **Main success scenario** | 1. User submits authentication credentials or initiates single sign-on provider login.<br>2. Authentication service validates credentials and issues secure session token.<br>3. System synchronizes user identity with application profile store.<br>4. System hydrates user session state with saved preferences, favorites, and history.<br>5. System redirects user to authenticated dashboard. |
| **Extensions** | **2a. Invalid email or password credentials provided:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays authentication failure notice.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System allows user to retry or request password reset.<br>**2b. Third-party single sign-on provider returns authentication error:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user of third-party login failure.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System offers standard email login alternative.<br>**3a. Profile synchronization fails:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System establishes guest fallback session and prompts user to reconnect. |
| **Postconditions** | User is authenticated and account profile is active across all application pages. |

---

## UC11: Bookmark Favorite Dish

| Part | Content |
|---|---|
| **Name** | Bookmark favorite dish |
| **Primary actor** | Authenticated User |
| **Stakeholders & interests** | User (wants to easily find and reuse favorite meals later). |
| **Preconditions** | User is viewing a meal recommendation card. |
| **Trigger** | User chooses to bookmark/favorite the displayed dish. |
| **Main success scenario** | 1. User indicates desire to favorite the current meal.<br>2. System verifies active authenticated user session.<br>3. System associates the meal identifier with the user's saved account profile.<br>4. System updates visual favorite indicator to active state.<br>5. System adds meal to user's saved favorites list. |
| **Extensions** | **2a. Unauthenticated guest attempts to favorite a dish:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System presents login/registration prompt modal.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 Upon successful login, system completes bookmarking the selected dish.<br>**3a. Meal is already bookmarked in user profile:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System removes meal from favorites (toggle action) and updates visual indicator.<br>**3b. Storage service error during save:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays save error notice and retains prior bookmark state. |
| **Postconditions** | Meal is stored in user's persistent favorites collection. |

---

## UC12: Review Meal Spin History

| Part | Content |
|---|---|
| **Name** | Review meal spin history |
| **Primary actor** | Authenticated User |
| **Stakeholders & interests** | User (wants to see what meals were recommended previously and revisit recipes). |
| **Preconditions** | User is logged in and navigates to account history. |
| **Trigger** | User opens spin history section. |
| **Main success scenario** | 1. User opens history view.<br>2. System retrieves chronological record of user's past meal spins.<br>3. System displays history list with meal names, categories, and timestamps.<br>4. User selects an historical entry to review its recipe or dining options. |
| **Extensions** | **2a. User has zero recorded spins in history:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays empty state message with prompt to start a new spin.<br>**2b. History retrieval service times out:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays retry prompt and offers cached recent items if available. |
| **Postconditions** | Chronological history of past spins is presented to the user. |

---

## UC13: Manage Profile & Saved Dietary Preferences

| Part | Content |
|---|---|
| **Name** | Manage profile and dietary preferences |
| **Primary actor** | Authenticated User |
| **Stakeholders & interests** | User (wants default dietary preferences automatically loaded on every visit without manual setup). |
| **Preconditions** | User is logged in and on profile settings page. |
| **Trigger** | User updates display name or default dietary restriction preferences. |
| **Main success scenario** | 1. User modifies profile information and toggles default allergen exclusions.<br>2. User submits profile changes.<br>3. System validates profile fields and constraint values.<br>4. System updates persistent user profile record.<br>5. System applies updated default preferences to active user session.<br>6. System displays success confirmation notice. |
| **Extensions** | **3a. User submits invalid profile values:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System highlights invalid fields and displays guidance message.<br>**4a. Profile persistence fails due to network outage:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user that changes could not be saved and preserves form inputs. |
| **Postconditions** | User profile and default dietary preferences are updated and applied to future sessions. |

---

## UC14: Apply Quick Preference Power-Ups

| Part | Content |
|---|---|
| **Name** | Apply quick preference power-ups |
| **Primary actor** | Hungry User |
| **Stakeholders & interests** | User (wants immediate one-tap refinement for common criteria like Healthy, Cheap, or Fast). |
| **Preconditions** | User is on meal spin interface. |
| **Trigger** | User toggles one or more power-up pills (Healthy, Cheap, <=30m). |
| **Main success scenario** | 1. User selects a quick power-up modifier (e.g., Healthy, Cheap, or <=30m prep).<br>2. System activates visual highlight on selected power-up.<br>3. System recalculates candidate scoring weights and filter criteria based on active power-ups.<br>4. System updates candidate dish pool to prioritize matching dishes. |
| **Extensions** | **1a. User de-selects an active power-up:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System deactivates modifier and restores base scoring weights.<br>**3a. Selected power-up combination eliminates all candidate dishes in chosen category:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays warning that criteria are strict and offers closest partial matches. |
| **Postconditions** | Active power-up filters are applied to all subsequent spins in the session. |

---

## UC15: Share Party Room Invitation

| Part | Content |
|---|---|
| **Name** | Share party room invitation |
| **Primary actor** | Party Host |
| **Stakeholders & interests** | Host & Invitees (want effortless room link and code sharing across communication channels). |
| **Preconditions** | Party room is active. |
| **Trigger** | Host requests to copy party invite link or code. |
| **Main success scenario** | 1. Host requests party room share link or code.<br>2. System formats full invitation URL containing room join code.<br>3. System copies invitation text to host's clipboard.<br>4. System displays confirmation notice indicating link is copied. |
| **Extensions** | **3a. Device clipboard permissions are denied or unavailable:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays readable room code in highlighted text box with manual selection. |
| **Postconditions** | Room invitation link or code is copied for sharing. |

---

## UC16: Leave Active Party Room

| Part | Content |
|---|---|
| **Name** | Leave active party room |
| **Primary actor** | Party Member |
| **Stakeholders & interests** | Departing Member (wants clean exit from room); Remaining Members (want accurate room roster). |
| **Preconditions** | Member is inside an active party room. |
| **Trigger** | Member clicks leave party action or closes room session. |
| **Main success scenario** | 1. Member requests to leave party room.<br>2. System disconnects member from room's real-time communication channel.<br>3. System removes member from active room roster.<br>4. System broadcasts member left notification to remaining room participants.<br>5. System redirects departing member to main homepage. |
| **Extensions** | **1a. Host leaves party room with active members remaining:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System transfers host privileges to next senior member or concludes session.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System notifies remaining participants of host status change.<br>**2a. Disconnection happens abruptly (browser crash/network drop):**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 Real-time server detects heartbeat timeout.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System marks member as disconnected and updates roster for peers. |
| **Postconditions** | Member is cleanly disconnected and removed from active party roster. |

---

## UC17: Toggle UI Theme Mode

| Part | Content |
|---|---|
| **Name** | Toggle UI theme mode |
| **Primary actor** | End User |
| **Stakeholders & interests** | User (wants comfortable visual appearance in light or dark lighting environments). |
| **Preconditions** | System interface is loaded. |
| **Trigger** | User triggers theme toggle control. |
| **Main success scenario** | 1. User selects theme toggle action.<br>2. System switches active visual theme between Light and Dark modes.<br>3. System updates interface colors, contrast levels, and asset styling instantly.<br>4. System stores theme preference in client settings for future sessions. |
| **Extensions** | **4a. Client local preference storage is restricted:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System applies visual theme for current session without persistence error. |
| **Postconditions** | Application interface renders in selected visual theme mode. |

---

## UC18: Configure Multi-Dish Spin Quantity

| Part | Content |
|---|---|
| **Name** | Configure multi-dish spin quantity |
| **Primary actor** | Hungry User |
| **Stakeholders & interests** | User (wants multiple meal recommendations in a single spin to compare options). |
| **Preconditions** | User is on meal spin interface. |
| **Trigger** | User adjusts dish count control. |
| **Main success scenario** | 1. User selects desired quantity of dish recommendations (e.g., 1 to 4 dishes).<br>2. System validates requested count is within permitted range.<br>3. System configures multi-dish generation parameters.<br>4. User initiates spin.<br>5. System selects requested number of distinct dishes meeting active criteria.<br>6. System displays comparative grid of selected meal outcomes. |
| **Extensions** | **2a. User inputs quantity below minimum or above maximum limit:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System clamps input value to allowed range (e.g., 1 to 4) and alerts user.<br>**5a. Candidate pool has fewer unique matching dishes than requested count:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System returns all available matching unique dishes without duplicates.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System informs user of limited candidate count. |
| **Postconditions** | Configured quantity of distinct meal recommendations is presented. |

---

## UC19: Remove Saved Meal from Favorites

| Part | Content |
|---|---|
| **Name** | Remove saved meal from favorites |
| **Primary actor** | Authenticated User |
| **Stakeholders & interests** | User (wants to keep favorites list curated and remove unwanted items). |
| **Preconditions** | User is viewing saved favorites list containing at least one saved meal. |
| **Trigger** | User chooses to remove a specific dish from favorites. |
| **Main success scenario** | 1. User selects remove action on a saved favorite dish.<br>2. System verifies user session and ownership of bookmark.<br>3. System deletes meal bookmark association from user's account profile.<br>4. System removes dish item from favorites view with smooth transition.<br>5. System displays confirmation notice. |
| **Extensions** | **2a. Session expires during removal action:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System prompts user to re-authenticate and retains list state.<br>**3a. Persistent storage error occurs during deletion:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System alerts user that removal failed and prompts to retry.<br>**4a. User removes last remaining saved meal in list:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System transitions favorites view to clean empty-state display. |
| **Postconditions** | Specified meal is deleted from user's persistent favorites. |

---

## UC20: Inspect Dish Details & Ingredients

| Part | Content |
|---|---|
| **Name** | Inspect dish details and ingredients |
| **Primary actor** | Home Cook |
| **Stakeholders & interests** | Home Cook (wants full nutritional breakdown, allergen profile, and ingredient quantities before choosing). |
| **Preconditions** | A dish recommendation or catalog item is selected. |
| **Trigger** | User opens detailed dish inspection view. |
| **Main success scenario** | 1. User requests detailed information for a specific dish.<br>2. System retrieves comprehensive dish metadata including description, prep time, cuisine classification, and allergen tags.<br>3. System retrieves complete itemized ingredient breakdown.<br>4. System renders full dish detail panel. |
| **Extensions** | **2a. Dish identifier is invalid or missing in catalog:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System displays error notification indicating dish not found.<br>&nbsp;&nbsp;&nbsp;&nbsp;.2 System navigates back to primary meal recommendation card.<br>**3a. Ingredient list is partially unavailable for specific legacy entry:**<br>&nbsp;&nbsp;&nbsp;&nbsp;.1 System renders available metadata and flags missing ingredient breakdown gracefully. |
| **Postconditions** | Full dish metadata, ingredients, and allergen breakdown are displayed. |
