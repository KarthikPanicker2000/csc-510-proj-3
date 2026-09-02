MealSlot Project 1a — Known-Defect Behavioral Pytest Raw Output
Command: C:\Users\hp\anaconda3\python.exe -m pytest -v --tb=short test_mealslot_known_defects.py
Result: 10 failed, exit code 1

============================= test session starts =============================
platform win32 -- Python 3.7.6, pytest-5.3.5, py-1.8.1, pluggy-0.13.1 -- C:\Users\hp\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\hp\Documents\Codex\2026-08-30\i-x20
collecting ... collected 10 items

test_mealslot_known_defects.py::test_incompatible_party_diets_should_raise_a_conflict FAILED [ 10%]
test_mealslot_known_defects.py::test_party_fallback_should_exclude_dishes_with_group_allergens FAILED [ 20%]
test_mealslot_known_defects.py::test_whitespace_only_party_nickname_should_be_rejected FAILED [ 30%]
test_mealslot_known_defects.py::test_repeated_join_should_not_create_a_duplicate_membership FAILED [ 40%]
test_mealslot_known_defects.py::test_leaving_from_the_page_should_remove_the_authoritative_membership FAILED [ 50%]
test_mealslot_known_defects.py::test_guest_should_be_able_to_browse_a_locally_saved_meal FAILED [ 60%]
test_mealslot_known_defects.py::test_failed_account_save_should_revert_the_optimistic_saved_state FAILED [ 70%]
test_mealslot_known_defects.py::test_party_chat_should_deliver_the_message_to_another_browser FAILED [ 80%]
test_mealslot_known_defects.py::test_default_title_case_category_should_find_seeded_dishes FAILED [ 90%]
test_mealslot_known_defects.py::test_join_page_should_retain_the_returned_member_identifier FAILED [100%]

================================== FAILURES ===================================
____________ test_incompatible_party_diets_should_raise_a_conflict ____________
test_mealslot_known_defects.py:87: in test_incompatible_party_diets_should_raise_a_conflict
    assert result["conflict"] is True, (
E   AssertionError: Expected incompatible party diets to be reported as a conflict, but current behavior selected ['vegan'] with conflict=False.
E   assert False is True
_______ test_party_fallback_should_exclude_dishes_with_group_allergens ________
test_mealslot_known_defects.py:105: in test_party_fallback_should_exclude_dishes_with_group_allergens
    assert all("peanut" not in dish["allergens"] for dish in results), (
E   AssertionError: Expected the group peanut exclusion to apply to fallback dishes, but current fallback returned ['unsafe', 'safe1', 'safe2'].
E   assert False
E    +  where False = all(<generator object test_party_fallback_should_exclude_dishes_with_group_allergens.<locals>.<genexpr> at 0x0000014049A0A4C8>)
___________ test_whitespace_only_party_nickname_should_be_rejected ____________
test_mealslot_known_defects.py:118: in test_whitespace_only_party_nickname_should_be_rejected
    assert status == 400, (
E   AssertionError: Expected a whitespace-only nickname to be rejected with status 400, but current route-style validation accepts it with status 200.
E   assert 200 == 400
E     -200
E     +400
_________ test_repeated_join_should_not_create_a_duplicate_membership _________
test_mealslot_known_defects.py:134: in test_repeated_join_should_not_create_a_duplicate_membership
    assert second_status == 409, (
E   AssertionError: Expected the repeated join to be rejected as an existing membership, but it returned 200 and created 3 total members.
E   assert 200 == 409
E     -200
E     +409
____ test_leaving_from_the_page_should_remove_the_authoritative_membership ____
test_mealslot_known_defects.py:149: in test_leaving_from_the_page_should_remove_the_authoritative_membership
    assert "m2" not in [member["id"] for member in remaining], (
E   AssertionError: Expected Leave Party to delete member m2 from authoritative state, but current page behavior left ['m1', 'm2'].
E   assert 'm2' not in ['m1', 'm2']
__________ test_guest_should_be_able_to_browse_a_locally_saved_meal ___________
test_mealslot_known_defects.py:162: in test_guest_should_be_able_to_browse_a_locally_saved_meal
    assert visible == ["dish1"], (
E   AssertionError: Expected the guest's locally saved dish to appear in Favorites, but the signed-out page exposed [].
E   assert [] == ['dish1']
E     Right contains one more item: 'dish1'
E     Full diff:
E     - []
E     + ['dish1']
______ test_failed_account_save_should_revert_the_optimistic_saved_state ______
test_mealslot_known_defects.py:175: in test_failed_account_save_should_revert_the_optimistic_saved_state
    assert visible == [], (
E   AssertionError: Expected a failed account persistence request to restore the prior UI state, but the optimistic collection remained ['dish1'].
E   assert ['dish1'] == []
E     Left contains one more item: 'dish1'
E     Full diff:
E     - ['dish1']
E     + []
________ test_party_chat_should_deliver_the_message_to_another_browser ________
test_mealslot_known_defects.py:189: in test_party_chat_should_deliver_the_message_to_another_browser
    assert remote == ["Pizza?"], (
E   AssertionError: Expected the remote party browser to receive the chat message, but current protocol behavior produced remote log [].
E   assert [] == ['Pizza?']
E     Right contains one more item: 'Pizza?'
E     Full diff:
E     - []
E     + ['Pizza?']
_________ test_default_title_case_category_should_find_seeded_dishes __________
test_mealslot_known_defects.py:202: in test_default_title_case_category_should_find_seeded_dishes
    assert matches, (
E   AssertionError: Expected the default Breakfast selection to find seeded breakfast dishes, but exact case-sensitive matching returned no candidates.
E   assert []
_________ test_join_page_should_retain_the_returned_member_identifier _________
test_mealslot_known_defects.py:216: in test_join_page_should_retain_the_returned_member_identifier
    assert page_state["memberId"] == "m2", (
E   AssertionError: Expected the joined browser to retain memberId m2 for realtime operations, but current page state stored None.
E   assert None == 'm2'
E     -None
E     +'m2'
============================= 10 failed in 0.19s ==============================
PYTEST_EXIT_CODE=1

