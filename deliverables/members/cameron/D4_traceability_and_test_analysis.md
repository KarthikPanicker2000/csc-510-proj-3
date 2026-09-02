# Deliverable D4: Traceability Matrix & Test Suite Analysis

## Part 1: Comprehensive Traceability Matrix (Our Tests)

The table below maps each of our 20 custom-designed E2E tests (`TC01`–`TC20`) to the reverse-engineered Use Cases (`UC1`–`UC20`).

| Use Case | Covered by Our Custom Test | What the Test Proves |
|---|---|---|
| **UC1: Spin Single Meal** | `TC01` | Asserts `/api/spin` returns valid HTTP response when active. |
| **UC2: Plan Full-Day Meals** | `TC02` | Asserts batch meal generation constraints. |
| **UC3: Filter Dietary Restrictions** | `TC03` | Asserts constraint payload filters responses appropriately. |
| **UC4: View Recipes & Tutorial** | `TC04` | Asserts recipe fetch endpoint payload shape. |
| **UC5: Locate Dining Venues** | `TC05` | Asserts `/api/places` proxy connectivity. |
| **UC6: Create Group Party Room** | `TC06` | Asserts party creation API and DB integrity. |
| **UC7: Join Existing Party Room** | `TC07` | Proves invalid join codes are rejected cleanly (PASS). |
| **UC8: Synchronize Group Spin** | `TC08` | Asserts socket event payload delivery. |
| **UC9: Exchange Realtime Chat** | `TC09` | Asserts chat message payload propagation. |
| **UC10: Authenticate User Account** | `TC10` | Proves `/api/user/create` rejects unauthenticated users (PASS). |
| **UC11: Bookmark Favorite Dish** | `TC11` | Asserts favorite save logic. |
| **UC12: Review Meal Spin History** | `TC12` | Asserts history array retrieval logic. |
| **UC13: Manage Dietary Profile** | `TC13` | Asserts profile update propagation. |
| **UC14: Apply Quick Power-Ups** | `TC14` | Asserts modifier payload alters spin criteria. |
| **UC15: Share Party Room Invite** | `TC15` | Asserts link formatting generation. |
| **UC16: Leave Active Party Room** | `TC16` | Asserts leave party endpoint connectivity. |
| **UC17: Toggle UI Theme Mode** | `TC17` | Asserts client theme state toggle. |
| **UC18: Configure Spin Quantity** | `TC18` | Asserts quantity parameter logic. |
| **UC19: Remove Saved Favorite** | `TC19` | Asserts favorite removal endpoint logic. |
| **UC20: Inspect Dish Details** | `TC20` | Proves invalid dish lookups fail gracefully (PASS). |

---

## Part 2: Critical Evaluation of MealSlot's Existing Test Suite

MealSlot (`fixmeseb/mealslots`) possesses an unusually thorough prior test suite comprising **73 test files** and **390 individual test cases** executing under Vitest and React Testing Library. 

### Does the project's test suite cover the use cases?
Yes. The existing Vitest suite successfully covers all 20 of our reverse-engineered use cases at the unit and component level. For instance, `UC1` is covered by `tests/app/api/spin.route.test.ts`, and `UC3` is exhaustively covered by `tests/lib/allergens.test.ts` and `tests/components/FilterMenu.test.tsx`.

### Where are the project's own tests blind?
Despite having 390 test cases, the test suite exhibits key blind spots:
1. **Google Maps SDK Initialization Race Conditions (`UC5`):** Tests mock instant map availability, missing map loading timing errors in real browsers. During our LLM inspection, we found `PartyMap.test.tsx` hides a real race condition where `TypeError: map.setCenter is not a function` is thrown if geolocation fires before the Google Maps SDK fully loads.
2. **WebSocket Network Dropouts (`UC9`, `UC16`):** Tests emit socket events in isolation (`realtime.test.ts`), but do not test behavior during intermittent WebSocket disconnections or out-of-order message arrivals.
3. **External API Quota Exceeded Testing (`UC4`, `UC5`):** Tests mock successful Google Places and YouTube API responses, but lack explicit tests for HTTP 429 Quota Exceeded error payloads from third-party APIs.
