# MealSlot D3 — Known-Defect Behavioral Test Results

**Command:** `C:\Users\hp\anaconda3\python.exe -m pytest -v --tb=short test_mealslot_known_defects.py`  
**Summary:** 10 executed — 0 PASS, 10 FAIL, 0 BLOCKED  
**Exit code:** 1  
**Product behavior changes:** None

## Important interpretation

These tests assert the expected behavior described by the use cases against small Python models of inspected MealSlot implementation paths. A failure records a specification-versus-implementation discrepancy. The assertions are not fabricated with `assert False`.

They are useful for explaining known defects and producing readable pytest failure output, but they do not replace the live Playwright/API evidence because they do not start the actual MealSlot application.

## Results

| Test | Use case | Why we tried it | Expected | What happened | Result | Explanation |
|---|---|---|---|---|---|---|
| `test_incompatible_party_diets_should_raise_a_conflict` | UC02 — Set Party Dietary Preferences | Verify that incompatible group diets are explicitly reported. | Vegan and omnivore preferences produce a conflict. | The merge selected vegan and returned `conflict=False`. | **FAIL** | Current merge logic always selects the strictest ethic diet, making this conflict path unreachable. |
| `test_party_fallback_should_exclude_dishes_with_group_allergens` | UC04 — Spin the Party Slot Machine | Allergen exclusions must remain effective during fallback behavior. | A peanut-excluding party receives no peanut fallback dish. | The modeled fallback returned `unsafe`, `safe1`, and `safe2`, including the peanut dish. | **FAIL** | The fallback menu is used without applying merged allergen exclusions. |
| `test_whitespace_only_party_nickname_should_be_rejected` | UC16 — Create Party | Validate a meaningful host nickname before creating party data. | Whitespace-only nickname returns status 400. | Length-only route validation accepted it with status 200. | **FAIL** | Server-side validation does not trim the nickname before checking its length. |
| `test_repeated_join_should_not_create_a_duplicate_membership` | UC17 — Join Party | Prevent the same participant from creating repeated memberships. | Second join is rejected with a conflict response. | Both joins returned 200 and the roster grew to three records. | **FAIL** | The join path does not enforce unique party membership. |
| `test_leaving_from_the_page_should_remove_the_authoritative_membership` | UC14 — Leave a Party | Ensure Leave Party changes server-authoritative membership. | Departing member `m2` is absent afterward. | Local state cleared, but authoritative members remained `m1` and `m2`. | **FAIL** | The inspected page resets locally without invoking the implemented leave endpoint. |
| `test_guest_should_be_able_to_browse_a_locally_saved_meal` | UC08 — Save a Meal to Favorites | Confirm that guest-local saves can be revisited as the use case claims. | Favorites displays locally saved `dish1`. | The signed-out Favorites behavior exposed an empty collection. | **FAIL** | Guest saves use local storage, while the Favorites page requires authentication. |
| `test_failed_account_save_should_revert_the_optimistic_saved_state` | UC08 — Save a Meal to Favorites | Keep displayed and persisted saved state consistent after failure. | Failed persistence restores the prior empty collection. | The optimistic collection continued to contain `dish1`. | **FAIL** | The current home-page failure path logs the error without rolling back optimistic state. |
| `test_party_chat_should_deliver_the_message_to_another_browser` | UC20 — Chat with Party Members | Verify the central value of realtime party chat. | The remote browser receives `Pizza?`. | Only the sender log contained the message; the remote log was empty. | **FAIL** | The inspected raw-WebSocket client protocol does not match the Socket.IO server protocol. |
| `test_default_title_case_category_should_find_seeded_dishes` | UC01 — Spin for a Meal | Verify that the application’s default categories work with its supplied data. | `Breakfast` finds seeded breakfast dishes. | Exact case-sensitive matching returned no candidates. | **FAIL** | The UI uses title case while the seed data stores lowercase categories. |
| `test_join_page_should_retain_the_returned_member_identifier` | UC17 — Join Party | Joined members need their identity for preferences, voting, and realtime behavior. | Page state retains returned member ID `m2`. | Page state stored `memberId=None`. | **FAIL** | The join page discards the membership identifier returned by the join operation. |

## Recommended demo selection

The clearest single failure for narration is:

`test_default_title_case_category_should_find_seeded_dishes`

Suggested explanation: “This test fails because MealSlot sends `Breakfast` from the interface while the supplied database stores `breakfast`, and the lookup is case-sensitive. We documented the defect without changing the cloned application.”
