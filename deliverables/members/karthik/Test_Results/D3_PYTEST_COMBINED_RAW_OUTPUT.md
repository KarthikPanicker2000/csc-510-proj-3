# MealSlot D3 — Combined Pytest Raw Output

**Summary:** 114 tests executed — 104 PASS, 10 FAIL  
**Product behavior changes:** None


```text
MealSlot Project 1a — Combined Pytest Raw Output
Generated from the exact two files supplied by the user.

======================================================================
SUITE A: C:\Users\hp\Downloads\test_top20_use_cases (1).py
COMMAND: C:\Users\hp\anaconda3\python.exe -m pytest -v --tb=short "C:\Users\hp\Downloads\test_top20_use_cases (1).py"
======================================================================
============================= test session starts =============================
platform win32 -- Python 3.7.6, pytest-5.3.5, py-1.8.1, pluggy-0.13.1 -- C:\Users\hp\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\hp\Downloads
collecting ... collected 63 items

test_top20_use_cases (1).py::test_spinning_returns_one_dish_per_reel_from_the_offered_candidates PASSED [  1%]
test_top20_use_cases (1).py::test_a_slot_with_no_matching_dishes_gets_a_no_options_placeholder_instead_of_failing PASSED [  3%]
test_top20_use_cases (1).py::test_spinning_again_before_the_cooldown_expires_is_rejected PASSED [  4%]
test_top20_use_cases (1).py::test_merging_preferences_unions_allergens_and_keeps_the_strictest_diet PASSED [  6%]
test_top20_use_cases (1).py::test_mixing_vegan_and_omnivore_preferences_never_actually_raises_a_conflict_flag PASSED [  7%]
test_top20_use_cases (1).py::test_vegan_diet_combined_with_three_or_more_blocked_allergens_is_flagged_as_a_conflict PASSED [  9%]
test_top20_use_cases (1).py::test_keep_votes_reaching_a_majority_of_connected_members_lock_the_slot PASSED [ 11%]
test_top20_use_cases (1).py::test_changing_a_vote_before_quorum_replaces_the_previous_vote_instead_of_adding_to_it PASSED [ 12%]
test_top20_use_cases (1).py::test_a_disconnected_voter_no_longer_counts_toward_the_live_quorum PASSED [ 14%]
test_top20_use_cases (1).py::test_a_party_spin_fills_all_three_slots_and_keeps_locked_dishes_in_place PASSED [ 15%]
test_top20_use_cases (1).py::test_a_failing_internal_spin_falls_back_to_the_hardcoded_menu PASSED [ 17%]
test_top20_use_cases (1).py::test_a_slot_still_unfilled_after_six_attempts_gets_a_no_options_placeholder PASSED [ 19%]
test_top20_use_cases (1).py::test_a_locked_slot_keeps_its_dish_while_other_slots_get_new_ones PASSED [ 20%]
test_top20_use_cases (1).py::test_a_legacy_index_only_lock_is_ignored_and_the_slot_is_re_spun PASSED [ 22%]
test_top20_use_cases (1).py::test_deduplication_can_leave_fewer_than_three_unique_dishes_without_crashing PASSED [ 23%]
test_top20_use_cases (1).py::test_a_changed_display_name_is_pushed_to_the_database_on_the_next_poll PASSED [ 25%]
test_top20_use_cases (1).py::test_an_unchanged_display_name_triggers_no_database_call PASSED [ 26%]
test_top20_use_cases (1).py::test_a_failed_database_update_leaves_the_previously_synced_name_in_place PASSED [ 28%]
test_top20_use_cases (1).py::test_a_configured_api_key_returns_up_to_two_normalized_video_results PASSED [ 30%]
test_top20_use_cases (1).py::test_a_missing_api_key_returns_a_deterministic_stub_video_instead_of_an_empty_modal PASSED [ 31%]
test_top20_use_cases (1).py::test_a_video_search_failure_for_one_dish_does_not_affect_other_dishes PASSED [ 33%]
test_top20_use_cases (1).py::test_an_authenticated_user_saving_a_dish_persists_it_to_their_account PASSED [ 34%]
test_top20_use_cases (1).py::test_a_failed_persistence_request_reverts_the_saved_state PASSED [ 36%]
test_top20_use_cases (1).py::test_a_guests_locally_saved_meals_are_not_carried_into_an_authenticated_profile PASSED [ 38%]
test_top20_use_cases (1).py::test_dishes_containing_an_excluded_allergen_are_removed_from_results PASSED [ 39%]
test_top20_use_cases (1).py::test_excluding_every_dish_in_a_category_still_yields_a_placeholder_via_the_spin_engine PASSED [ 41%]
test_top20_use_cases (1).py::test_a_signed_in_users_saved_allergens_preselect_the_filter_menu PASSED [ 42%]
test_top20_use_cases (1).py::test_registering_with_a_new_auth_id_creates_a_user_record PASSED [ 44%]
test_top20_use_cases (1).py::test_registering_with_an_auth_id_that_already_exists_returns_the_existing_record_unchanged PASSED [ 46%]
test_top20_use_cases (1).py::test_a_missing_auth_id_creates_no_database_record PASSED [ 47%]
test_top20_use_cases (1).py::test_the_healthy_powerup_gives_a_healthy_dish_a_higher_score_than_an_unhealthy_one PASSED [ 49%]
test_top20_use_cases (1).py::test_combining_healthy_and_cheap_powerups_multiplies_their_individual_effects PASSED [ 50%]
test_top20_use_cases (1).py::test_no_dish_matching_an_active_powerup_still_yields_a_selection_instead_of_failing PASSED [ 52%]
test_top20_use_cases (1).py::test_saved_ids_are_resolved_against_the_current_catalog_and_can_be_filtered_by_category PASSED [ 53%]
test_top20_use_cases (1).py::test_a_saved_id_no_longer_in_the_catalog_is_silently_omitted PASSED [ 55%]
test_top20_use_cases (1).py::test_an_account_with_no_saved_meals_resolves_to_an_empty_list PASSED [ 57%]
test_top20_use_cases (1).py::test_removing_a_saved_dish_updates_and_persists_the_shortened_list PASSED [ 58%]
test_top20_use_cases (1).py::test_a_failed_removal_request_keeps_the_dish_in_the_prior_collection PASSED [ 60%]
test_top20_use_cases (1).py::test_removing_the_last_saved_meal_leaves_an_empty_collection PASSED [ 61%]
test_top20_use_cases (1).py::test_leaving_a_party_removes_that_members_record_and_keeps_the_rest PASSED [ 63%]
test_top20_use_cases (1).py::test_the_host_leaving_implicitly_hands_off_to_the_next_connected_member PASSED [ 65%]
test_top20_use_cases (1).py::test_a_member_who_never_left_keeps_their_membership_when_removal_is_only_attempted PASSED [ 66%]
test_top20_use_cases (1).py::test_venues_are_returned_per_cuisine_using_the_provided_coordinates PASSED [ 68%]
test_top20_use_cases (1).py::test_missing_coordinates_fall_back_to_geocoding_the_location_hint PASSED [ 69%]
test_top20_use_cases (1).py::test_one_cuisines_search_failure_does_not_prevent_other_cuisines_from_returning_results PASSED [ 71%]
test_top20_use_cases (1).py::test_a_valid_nickname_creates_an_active_party_with_the_creator_as_host PASSED [ 73%]
test_top20_use_cases (1).py::test_an_empty_nickname_prevents_party_creation PASSED [ 74%]
test_top20_use_cases (1).py::test_a_hosts_saved_account_allergens_seed_the_new_partys_host_preferences PASSED [ 76%]
test_top20_use_cases (1).py::test_joining_with_a_valid_code_adds_a_new_member_to_the_active_party PASSED [ 77%]
test_top20_use_cases (1).py::test_joining_with_an_unknown_or_inactive_code_is_rejected PASSED [ 79%]
test_top20_use_cases (1).py::test_joining_without_stated_preferences_stores_default_empty_preferences PASSED [ 80%]
test_top20_use_cases (1).py::test_valid_credentials_establish_a_session_and_load_the_matching_profile PASSED [ 82%]
test_top20_use_cases (1).py::test_invalid_credentials_are_rejected_without_creating_a_session PASSED [ 84%]
test_top20_use_cases (1).py::test_a_first_time_valid_identity_gets_a_fresh_empty_profile_instead_of_being_blocked PASSED [ 85%]
test_top20_use_cases (1).py::test_signing_out_clears_the_session_profile_and_client_cache PASSED [ 87%]
test_top20_use_cases (1).py::test_a_failed_provider_sign_out_does_not_falsely_report_success PASSED [ 88%]
test_top20_use_cases (1).py::test_after_sign_out_an_account_only_page_exposes_no_previous_users_data PASSED [ 90%]
test_top20_use_cases (1).py::test_a_non_empty_message_is_broadcast_to_connected_party_members PASSED [ 92%]
test_top20_use_cases (1).py::test_sending_an_empty_message_does_nothing PASSED [ 93%]
test_top20_use_cases (1).py::test_without_a_dedicated_realtime_server_a_message_only_reaches_local_browser_tabs PASSED [ 95%]
test_top20_use_cases (1).py::test_saving_new_allergen_selections_persists_them_to_the_account PASSED [ 96%]
test_top20_use_cases (1).py::test_a_failed_save_leaves_the_prior_allergen_list_active PASSED [ 98%]
test_top20_use_cases (1).py::test_saved_account_allergens_are_applied_to_a_spin_without_reselecting_them PASSED [100%]

============================== warnings summary ===============================
C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137
  C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137: PytestCacheWarning: could not create cache path C:\Users\hp\Downloads\.pytest_cache\v\cache\stepwise
    self.warn("could not create cache path {path}", path=path)

C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137
  C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137: PytestCacheWarning: could not create cache path C:\Users\hp\Downloads\.pytest_cache\v\cache\nodeids
    self.warn("could not create cache path {path}", path=path)

-- Docs: https://docs.pytest.org/en/latest/warnings.html
======================= 63 passed, 2 warnings in 0.30s ========================
PYTEST_EXIT_CODE=0

======================================================================
SUITE B: C:\Users\hp\Desktop\SE Project 1a\test_top20_use_cases_additional.py
COMMAND: C:\Users\hp\anaconda3\python.exe -m pytest -v --tb=short "C:\Users\hp\Desktop\SE Project 1a\test_top20_use_cases_additional.py"
======================================================================
============================= test session starts =============================
platform win32 -- Python 3.7.6, pytest-5.3.5, py-1.8.1, pluggy-0.13.1 -- C:\Users\hp\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\hp\Desktop\SE Project 1a
collecting ... collected 41 items

test_top20_use_cases_additional.py::test_spin_request_with_a_missing_category_is_rejected_before_selection PASSED [  2%]
test_top20_use_cases_additional.py::test_spin_with_multiple_candidates_uses_the_injected_random_position PASSED [  4%]
test_top20_use_cases_additional.py::test_merging_no_party_preferences_produces_no_invented_constraints PASSED [  7%]
test_top20_use_cases_additional.py::test_duplicate_party_allergens_are_deduplicated_and_sorted PASSED [  9%]
test_top20_use_cases_additional.py::test_reroll_votes_reaching_quorum_release_the_slot_for_another_spin PASSED [ 12%]
test_top20_use_cases_additional.py::test_vote_below_quorum_leaves_the_slot_undecided PASSED [ 14%]
test_top20_use_cases_additional.py::test_party_fallback_is_used_without_filtering_its_allergens PASSED [ 17%]
test_top20_use_cases_additional.py::test_party_spin_never_reuses_a_dish_already_held_in_a_locked_slot PASSED [ 19%]
test_top20_use_cases_additional.py::test_lock_for_a_dish_absent_from_the_current_reel_is_ignored PASSED [ 21%]
test_top20_use_cases_additional.py::test_lock_with_an_out_of_range_slot_index_cannot_affect_valid_reels PASSED [ 24%]
test_top20_use_cases_additional.py::test_missing_provider_display_name_skips_database_synchronization PASSED [ 26%]
test_top20_use_cases_additional.py::test_name_sync_can_succeed_on_a_later_poll_after_a_transient_failure PASSED [ 29%]
test_top20_use_cases_additional.py::test_successful_video_search_with_no_matches_returns_an_empty_group PASSED [ 31%]
test_top20_use_cases_additional.py::test_video_result_order_is_preserved_when_limited_to_two_items PASSED [ 34%]
test_top20_use_cases_additional.py::test_guest_save_updates_local_collection_without_calling_account_persistence PASSED [ 36%]
test_top20_use_cases_additional.py::test_selecting_an_already_saved_heart_toggles_the_dish_out_of_favorites PASSED [ 39%]
test_top20_use_cases_additional.py::test_allergen_exclusion_is_case_insensitive PASSED [ 41%]
test_top20_use_cases_additional.py::test_dish_is_excluded_when_any_one_of_its_multiple_allergens_matches PASSED [ 43%]
test_top20_use_cases_additional.py::test_two_distinct_authentication_identities_create_isolated_profiles PASSED [ 46%]
test_top20_use_cases_additional.py::test_registration_without_a_display_name_still_links_the_auth_identity PASSED [ 48%]
test_top20_use_cases_additional.py::test_max_thirty_minutes_powerup_scores_a_fast_dish_above_a_slow_dish PASSED [ 51%]
test_top20_use_cases_additional.py::test_disabling_all_powerups_restores_equal_base_scores PASSED [ 53%]
test_top20_use_cases_additional.py::test_saved_meals_are_resolved_in_the_users_saved_order PASSED [ 56%]
test_top20_use_cases_additional.py::test_category_filter_with_no_matches_does_not_modify_saved_collection PASSED [ 58%]
test_top20_use_cases_additional.py::test_removing_an_unknown_saved_id_persists_the_unchanged_collection PASSED [ 60%]
test_top20_use_cases_additional.py::test_removing_one_duplicate_reference_eliminates_all_matching_references PASSED [ 63%]
test_top20_use_cases_additional.py::test_last_member_leaving_produces_an_empty_party_with_no_computed_host PASSED [ 65%]
test_top20_use_cases_additional.py::test_current_local_leave_behavior_does_not_remove_authoritative_membership PASSED [ 68%]
test_top20_use_cases_additional.py::test_failed_geocoding_still_allows_places_results_without_an_origin PASSED [ 70%]
test_top20_use_cases_additional.py::test_empty_cuisine_list_performs_no_places_or_geocoding_work_with_coordinates PASSED [ 73%]
test_top20_use_cases_additional.py::test_nickname_longer_than_twenty_four_characters_is_rejected PASSED [ 75%]
test_top20_use_cases_additional.py::test_whitespace_only_nickname_is_accepted_by_the_current_create_route_model PASSED [ 78%]
test_top20_use_cases_additional.py::test_party_code_collision_reports_creation_failure_without_overwriting_existing_party PASSED [ 80%]
test_top20_use_cases_additional.py::test_joining_with_a_code_of_the_wrong_length_is_rejected_before_lookup PASSED [ 82%]
test_top20_use_cases_additional.py::test_repeated_join_requests_create_duplicate_memberships_in_current_behavior PASSED [ 85%]
test_top20_use_cases_additional.py::test_authentication_provider_outage_creates_neither_session_nor_profile PASSED [ 87%]
test_top20_use_cases_additional.py::test_signing_in_as_another_identity_never_returns_the_first_users_profile PASSED [ 90%]
test_top20_use_cases_additional.py::test_signing_out_twice_is_idempotent PASSED [ 92%]
test_top20_use_cases_additional.py::test_sign_out_does_not_delete_unrelated_guest_preferences PASSED [ 95%]
test_top20_use_cases_additional.py::test_duplicate_realtime_chat_message_is_displayed_only_once PASSED [ 97%]
test_top20_use_cases_additional.py::test_chat_history_is_not_restored_after_a_new_party_client_session PASSED [100%]

============================== warnings summary ===============================
C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137
  C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137: PytestCacheWarning: could not create cache path C:\Users\hp\Desktop\SE Project 1a\.pytest_cache\v\cache\stepwise
    self.warn("could not create cache path {path}", path=path)

C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137
  C:\Users\hp\anaconda3\lib\site-packages\_pytest\cacheprovider.py:137: PytestCacheWarning: could not create cache path C:\Users\hp\Desktop\SE Project 1a\.pytest_cache\v\cache\nodeids
    self.warn("could not create cache path {path}", path=path)

-- Docs: https://docs.pytest.org/en/latest/warnings.html
======================= 41 passed, 2 warnings in 0.20s ========================
PYTEST_EXIT_CODE=0

======================================================================
COMBINED SUMMARY
======================================================================
104 tests executed
104 passed
0 failed
4 warnings (pytest could not create .pytest_cache in the read-only attachment folders)
```

## Raw output — 10 failing tests

```text
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
```

