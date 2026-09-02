# Deliverable D3: Test Code, Raw Output, & Results Table

## Code & Artifact Links
- **Our Designed API Test Suite:** [`test_e2e_usecases.py`](file:///Users/cameronegbert/Documents/NCSU/CSC510/group-10_deliverables/test_e2e_usecases.py)
- **Raw Execution Log:** [`raw_our_tests.txt`](file:///Users/cameronegbert/Documents/NCSU/CSC510/group-10_deliverables/raw_our_tests.txt)

---

## Test Execution Summary
- **Test Framework:** Python `unittest` (E2E API Request Harness)
- **Total Test Cases:** 20 designed test cases mapped 1:1 to UC1-UC20.
- **Execution Results:** 20 total (3 passed, 7 failed due to Next.js API rot, 10 skipped).

---

## Results Table: Our Designed E2E Test Cases

We designed a custom API testing suite targeting the MealSlot Next.js endpoints. As required, failures are reported honestly: the database and API routes have suffered code rot (returning HTTP 404/500), which our tests correctly caught.

| Test ID | Test Name (in `test_e2e_usecases.py`) | Why We Tried It | Expected Result | What Happened & Verdict |
|---|---|---|---|---|
| **TC01** | `test_uc01_spin_single_meal` | Verify single spin endpoint (`UC1`) | Returns HTTP 200 with dish | **FAIL.** API unreachable (HTTP 404). Server route rot. |
| **TC02** | `test_uc02_plan_full_day` | Test full-day generation (`UC2`) | Returns array of 4 distinct meals | **SKIP.** Complex state test skipped due to server offline. |
| **TC03** | `test_uc03_filter_dietary` | Test applying dietary filters (`UC3`) | Returns 200 and filtered dish array | **FAIL.** Failed to apply filters (HTTP 404). |
| **TC04** | `test_uc04_view_recipe` | Verify fetching recipe data (`UC4`) | Returns recipe object | **SKIP.** UI mapping required. |
| **TC05** | `test_uc05_locate_venues` | Test Google Places proxy (`UC5`) | Returns HTTP 200 with places | **FAIL.** Places API mock failed (HTTP 404). |
| **TC06** | `test_uc06_create_party` | Test party room creation (`UC6`) | Returns 200 and 6-char code | **FAIL.** Database offline / route dead. |
| **TC07** | `test_uc07_join_party_invalid` | Test invalid join code (`UC7`) | Returns 404 Not Found cleanly | **PASS.** Expected HTTP Error 404 triggered successfully. |
| **TC08** | `test_uc08_sync_group_spin` | Test Socket.IO sync (`UC8`) | Emits spin WebSocket event | **SKIP.** Requires WebSocket client. |
| **TC09** | `test_uc09_party_chat` | Test Socket.IO chat messaging (`UC9`) | Emits message WebSocket event | **SKIP.** Requires WebSocket client. |
| **TC10** | `test_uc10_missing_auth` | Test missing auth ID block (`UC10`) | Returns HTTP 400 Bad Request | **PASS.** Missing auth payload blocked cleanly. |
| **TC11** | `test_uc11_bookmark_favorite` | Test saving favorite (`UC11`) | Returns 200 | **SKIP.** Requires JWT. |
| **TC12** | `test_uc12_review_history` | Test spin history array (`UC12`) | Returns history array | **SKIP.** Requires JWT. |
| **TC13** | `test_uc13_manage_profile` | Test profile constraint update (`UC13`) | Returns 200 | **SKIP.** Requires JWT. |
| **TC14** | `test_uc14_power_ups` | Test healthy/cheap powerups (`UC14`) | Returns filtered results | **FAIL.** HTTP 404 on API endpoint. |
| **TC15** | `test_uc15_share_invite` | Test invite copy generation (`UC15`) | Returns formatted string | **SKIP.** Client-side UI logic. |
| **TC16** | `test_uc16_leave_party` | Test leaving party (`UC16`) | Returns 200 OK | **FAIL.** Leave API returned 404. |
| **TC17** | `test_uc17_theme_toggle` | Test localstorage theme switch (`UC17`) | Toggles theme state | **SKIP.** Client-side UI logic. |
| **TC18** | `test_uc18_multi_dish_quantity` | Test quantity configuration (`UC18`) | Returns array length matching quantity | **FAIL.** Multi-dish API returned 404. |
| **TC19** | `test_uc19_remove_favorite` | Test deleting favorite (`UC19`) | Returns 200 OK | **SKIP.** Requires JWT. |
| **TC20** | `test_uc20_dish_details` | Test fetching missing dish (`UC20`) | Returns HTTP 404 cleanly | **PASS.** Invalid dish lookup caught properly. |
