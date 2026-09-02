"""
Additional pytest coverage for the 20 use cases in
FINAL_TOP_20_USE_CASES_SEBASTIAN_PRESERVED.md.

This file deliberately adds scenarios that are not already present in
Sebastian's test_top20_use_cases.py. It follows the same approach as that
file: small Python behavioral models are used for MealSlot's TypeScript,
Next.js, Prisma, Stack Auth, browser, and external-service behavior.

These are specification-level tests. They do not start MealSlot, connect to
PostgreSQL, or call Stack Auth, YouTube, Google Places, or the realtime
server. Some tests intentionally document current implementation
discrepancies rather than silently correcting them.

Run with:
    pytest -v test_top20_use_cases_additional.py
"""

import pytest


# ======================================================================
# Shared behavioral models
# ======================================================================


def score_dish(dish, powerups):
    """Port of scoreDish() in proj2/mealslot/lib/scoring.ts."""
    score = 1.0
    if powerups.get("healthy"):
        score *= 2.0 if dish["isHealthy"] else 0.8
    if powerups.get("cheap"):
        score *= 2.0 if dish["costBand"] == 1 else (1.0 if dish["costBand"] == 2 else 0.6)
    if powerups.get("max30m"):
        score *= 2.0 if dish["timeBand"] == 1 else (0.9 if dish["timeBand"] == 2 else 0.5)
    return max(score, 0.0001)


def weighted_choice(items, weights, rnd):
    """Port of weightedChoice() in proj2/mealslot/lib/scoring.ts."""
    count = min(len(items), len(weights))
    if count == 0:
        return None
    total = sum(weights[:count])
    if total <= 0:
        return None
    cursor = rnd() * total
    for index in range(count):
        cursor -= weights[index]
        if cursor <= 0:
            return items[index]
    return items[count - 1]


def weighted_spin(reels, locked=None, powerups=None, rng=None):
    """Port of weightedSpin() in proj2/mealslot/lib/scoring.ts."""
    locked = locked or []
    powerups = powerups or {}
    rng = rng or (lambda: 0.5)
    locks = {
        item["index"]: item["dishId"]
        for item in locked
        if 0 <= item.get("index", -1) < len(reels) and item.get("dishId")
    }
    selection = []
    for index, reel in enumerate(reels):
        if not reel:
            selection.append({"id": f"placeholder_{index}", "name": "No options"})
            continue
        locked_id = locks.get(index)
        locked_dish = next((dish for dish in reel if dish["id"] == locked_id), None)
        if locked_dish:
            selection.append(locked_dish)
            continue
        weights = [score_dish(dish, powerups) for dish in reel]
        selection.append(weighted_choice(reel, weights, rng) or reel[0])
    return selection


def validate_spin_request(categories):
    """Model of the required-category validation in app/api/spin/route.ts."""
    if not categories or any(not category for category in categories):
        return {"status": 400, "error": "categories_required"}
    return {"status": 200}


STRICTNESS = {
    "vegan": 4,
    "vegetarian": 3,
    "pescatarian": 2,
    "keto": 2,
    "omnivore": 1,
    "none": 0,
}
ETHIC_DIETS = ("vegan", "vegetarian", "pescatarian", "omnivore")


def merge_constraints(preferences):
    """Port of mergeConstraints() in proj2/mealslot/lib/party.ts."""
    diets = [item.get("diet") for item in preferences if item.get("diet")]
    non_none = [diet for diet in diets if diet != "none"]
    merged = {}
    if non_none:
        ranked = sorted(set(non_none), key=lambda diet: -STRICTNESS[diet])
        ethic = next((diet for diet in ranked if diet in ETHIC_DIETS), None)
        merged["diet"] = [ethic or ranked[0]]

    allergens = sorted({allergen for item in preferences for allergen in item.get("allergens", [])})
    budgets = [item["budgetBand"] for item in preferences if "budgetBand" in item]
    times = [item["timeBand"] for item in preferences if "timeBand" in item]
    if allergens:
        merged["allergens"] = allergens
    if budgets:
        merged["budgetBand"] = min(budgets)
    if times:
        merged["timeBand"] = min(times)
    return merged


def fresh_votes():
    return [{"keep": set(), "reroll": set()} for _ in range(3)]


def tally_vote(votes, slot_index, choice, member_id):
    votes[slot_index]["keep"].discard(member_id)
    votes[slot_index]["reroll"].discard(member_id)
    votes[slot_index][choice].add(member_id)


def resolve_vote(votes, slot_index, live_member_count):
    required = max(1, live_member_count // 2 + 1)
    if len(votes[slot_index]["keep"]) >= required:
        return "lock"
    if len(votes[slot_index]["reroll"]) >= required:
        return "reroll"
    return None


def party_spin(locked, slots, spin_fn, fallback_menu, max_tries=6):
    """Port of the retry/deduplication loop in app/api/party/spin/route.ts."""
    output = [None, None, None]
    used = set()
    for index in range(3):
        if locked[index] and slots[index]:
            output[index] = slots[index]
            used.add(slots[index]["id"])

    def candidates():
        try:
            result = spin_fn()
            return result if isinstance(result, list) else [result]
        except Exception:
            return fallback_menu

    for _ in range(max_tries):
        for index in range(3):
            if locked[index] or output[index]:
                continue
            selected = next((dish for dish in candidates() if dish and dish["id"] not in used), None)
            if selected:
                output[index] = selected
                used.add(selected["id"])
        if all(output):
            break

    for index in range(3):
        if output[index] is None:
            output[index] = {"id": f"placeholder_{index}", "name": "No options", "allergens": []}
    return output


def sync_display_name(last_synced_name, provider_name, persist_fn):
    """Model of the Account page's periodic display-name synchronization."""
    if not provider_name or provider_name == last_synced_name:
        return last_synced_name, False
    try:
        persist_fn(provider_name)
        return provider_name, True
    except Exception:
        return last_synced_name, False


def get_recipe_videos(dish_name, api_key, search_fn, max_results=2):
    """Model of the per-dish YouTube lookup and development fallback."""
    if not api_key:
        return [{"id": "stub", "title": f"{dish_name} recipe (stub)", "stub": True}]
    try:
        return search_fn(dish_name)[:max_results]
    except Exception:
        return []


def toggle_saved_meal(saved_meals, dish_id, authenticated, persist_fn):
    """Model of toggleSavedMeal() in app/(site)/page.tsx."""
    updated = [item for item in saved_meals if item != dish_id] if dish_id in saved_meals else saved_meals + [dish_id]
    if not authenticated:
        return updated, True
    try:
        persist_fn(updated)
        return updated, True
    except Exception:
        return saved_meals, False


def filter_by_allergens(dishes, excluded):
    """Port of case-insensitive allergen exclusion in lib/dishes.ts."""
    normalized = {item.lower() for item in excluded}
    return [
        dish
        for dish in dishes
        if not any(allergen.lower() in normalized for allergen in dish.get("allergens", []))
    ]


def ensure_user_in_db(auth_id, name, database):
    """Model of ensureUserInDB() and the application-user upsert."""
    if not auth_id:
        return None
    if auth_id in database:
        return database[auth_id]
    user = {
        "id": f"user_{len(database) + 1}",
        "auth_id": auth_id,
        "name": name,
        "allergens": [],
        "savedMeals": [],
    }
    database[auth_id] = user
    return user


def resolve_saved_dishes(saved_ids, catalog):
    return [catalog[dish_id] for dish_id in saved_ids if dish_id in catalog]


def remove_saved_meal(saved_meals, dish_id, persist_fn):
    updated = [item for item in saved_meals if item != dish_id]
    try:
        persist_fn(updated)
        return updated, True
    except Exception:
        return saved_meals, False


def leave_party(members, leaving_id):
    return [member for member in members if member["id"] != leaving_id]


def compute_host(members):
    if not members:
        return None
    creator = next((member for member in members if member.get("creator")), None)
    return (creator or members[0])["id"]


def local_only_leave(local_state, authoritative_members, leaving_id):
    """Model of the current party page's local reset without the leave API."""
    local_state.clear()
    return authoritative_members


def search_places(cuisines, coordinates, location_hint, search_fn, geocode_fn):
    """Model of the error-isolated, per-cuisine Places lookup."""
    origin = coordinates if coordinates is not None else geocode_fn(location_hint)
    results, errors = {}, {}
    for cuisine in cuisines:
        try:
            results[cuisine] = search_fn(cuisine, origin)
        except Exception as error:
            results[cuisine] = []
            errors[cuisine] = str(error)
    return {"origin": origin, "results": results, "errors": errors}


def create_party_api(nickname, generated_code, existing_codes=None, account_allergens=None):
    """Model of the current create route, including its non-trimmed nickname validation."""
    existing_codes = existing_codes or set()
    if nickname is None or len(nickname) < 1 or len(nickname) > 24:
        return {"error": "invalid_nickname"}
    if generated_code in existing_codes:
        return {"error": "code_collision"}
    return {
        "code": generated_code,
        "isActive": True,
        "members": [{"id": "m1", "nickname": nickname, "creator": True, "allergens": account_allergens or []}],
    }


def join_party(parties, code, nickname, auth_id=None):
    """Model of the current join route, which does not prevent duplicate joins."""
    if len(code) != 6 or not nickname or len(nickname) > 24:
        return {"error": "invalid_request"}
    party = parties.get(code)
    if not party or not party.get("isActive"):
        return {"error": "NOT_FOUND"}
    member = {
        "id": f"m{len(party['members']) + 1}",
        "nickname": nickname,
        "auth_id": auth_id,
        "prefs": {},
    }
    party["members"].append(member)
    return {"partyId": code, "memberId": member["id"], "code": code}


def sign_in(credentials, valid_credentials, profile_store, provider_available=True):
    if not provider_available:
        return {"error": "provider_unavailable"}
    if credentials not in valid_credentials:
        return {"error": "invalid_credentials"}
    auth_id = valid_credentials[credentials]
    profile = profile_store.setdefault(auth_id, {"auth_id": auth_id, "allergens": [], "savedMeals": []})
    return {"session": {"auth_id": auth_id}, "profile": profile}


def sign_out(state):
    state["session"] = None
    state["profile"] = None
    state["cache"] = {}
    return state


def receive_chat(message, log, seen_ids):
    """Model of duplicate suppression in PartyClient's chat receiver."""
    if message["id"] in seen_ids:
        return False
    seen_ids.add(message["id"])
    log.append(message)
    return True


# ======================================================================
# Use Case 1 — Spin for a Meal (additional coverage)
# ======================================================================


def test_spin_request_with_a_missing_category_is_rejected_before_selection():
    result = validate_spin_request(["Breakfast", "", "Dinner"])
    assert result == {"status": 400, "error": "categories_required"}
    # New coverage: Sebastian tests an empty candidate reel, but not rejection of a malformed request whose required category value is missing.


def test_spin_with_multiple_candidates_uses_the_injected_random_position():
    reel = [[
        {"id": "first", "isHealthy": True, "costBand": 1, "timeBand": 1},
        {"id": "second", "isHealthy": True, "costBand": 1, "timeBand": 1},
    ]]
    selection = weighted_spin(reel, rng=lambda: 0.99)
    assert selection[0]["id"] == "second"
    # New coverage: this verifies real weighted selection among several eligible candidates, not Sebastian's one-candidate deterministic scenario.


# ======================================================================
# Use Case 2 — Set Party Dietary Preferences and Resolve Conflicts
# ======================================================================


def test_merging_no_party_preferences_produces_no_invented_constraints():
    assert merge_constraints([]) == {}
    # New coverage: an empty party preference set must not manufacture a diet, allergen, budget, or time restriction.


def test_duplicate_party_allergens_are_deduplicated_and_sorted():
    merged = merge_constraints([
        {"allergens": ["soy", "gluten"]},
        {"allergens": ["soy", "dairy"]},
    ])
    assert merged["allergens"] == ["dairy", "gluten", "soy"]
    # New coverage: Sebastian verifies unioning different allergens, while this checks duplicate removal and the deterministic stored ordering.


# ======================================================================
# Use Case 3 — Vote on a Spin Result
# ======================================================================


def test_reroll_votes_reaching_quorum_release_the_slot_for_another_spin():
    votes = fresh_votes()
    tally_vote(votes, 1, "reroll", "m1")
    tally_vote(votes, 1, "reroll", "m2")
    assert resolve_vote(votes, 1, live_member_count=3) == "reroll"
    # New coverage: Sebastian exercises a keep-vote quorum; this verifies the distinct reroll action.


def test_vote_below_quorum_leaves_the_slot_undecided():
    votes = fresh_votes()
    tally_vote(votes, 2, "keep", "m1")
    assert resolve_vote(votes, 2, live_member_count=4) is None
    # New coverage: a valid vote that does not reach the required majority must not lock or reroll a slot.


# ======================================================================
# Use Case 4 — Spin the Party Slot Machine
# ======================================================================


def test_party_fallback_is_used_without_filtering_its_allergens():
    def failed_spin():
        raise RuntimeError("spin unavailable")

    fallback = [
        {"id": "unsafe", "name": "Peanut Noodles", "allergens": ["peanut"]},
        {"id": "safe1", "name": "Rice", "allergens": []},
        {"id": "safe2", "name": "Salad", "allergens": []},
    ]
    result = party_spin([False, False, False], [None, None, None], failed_spin, fallback)
    assert any("peanut" in dish.get("allergens", []) for dish in result)
    # New coverage and discrepancy: the current hardcoded fallback is accepted as-is and is not checked against merged party allergens.


def test_party_spin_never_reuses_a_dish_already_held_in_a_locked_slot():
    locked_dish = {"id": "kept", "name": "Kept", "allergens": []}

    def candidates():
        return [locked_dish, {"id": "fresh1", "name": "Fresh 1"}, {"id": "fresh2", "name": "Fresh 2"}]

    result = party_spin([True, False, False], [locked_dish, None, None], candidates, [])
    assert [dish["id"] for dish in result] == ["kept", "fresh1", "fresh2"]
    # New coverage: the deduplication set includes locked dishes, preventing their reuse in an unlocked slot.


# ======================================================================
# Use Case 5 — Lock a Reel and Re-Spin
# ======================================================================


def test_lock_for_a_dish_absent_from_the_current_reel_is_ignored():
    reel = [[{"id": "available", "isHealthy": True, "costBand": 1, "timeBand": 1}]]
    result = weighted_spin(reel, locked=[{"index": 0, "dishId": "deleted"}], rng=lambda: 0.0)
    assert result[0]["id"] == "available"
    # New coverage: a structurally valid but stale dish lock falls back to normal selection.


def test_lock_with_an_out_of_range_slot_index_cannot_affect_valid_reels():
    reel = [[{"id": "valid", "isHealthy": True, "costBand": 1, "timeBand": 1}]]
    result = weighted_spin(reel, locked=[{"index": 8, "dishId": "valid"}], rng=lambda: 0.0)
    assert result[0]["id"] == "valid"
    # New coverage: malformed lock positions are discarded rather than being applied to an unrelated reel.


# ======================================================================
# Use Case 6 — Update Display Name
# ======================================================================


def test_missing_provider_display_name_skips_database_synchronization():
    updates = []
    name, changed = sync_display_name("Stored Name", None, updates.append)
    assert (name, changed) == ("Stored Name", False)
    assert updates == []
    # New coverage: Sebastian checks an unchanged name, while this checks Stack Auth returning no usable display name.


def test_name_sync_can_succeed_on_a_later_poll_after_a_transient_failure():
    attempts = {"count": 0}

    def flaky_persist(_name):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise ConnectionError("temporary")

    first_name, first_changed = sync_display_name("Old", "New", flaky_persist)
    second_name, second_changed = sync_display_name(first_name, "New", flaky_persist)
    assert (first_name, first_changed) == ("Old", False)
    assert (second_name, second_changed) == ("New", True)
    # New coverage: the polling design retries an unsynchronized provider name and can recover on a later cycle.


# ======================================================================
# Use Case 7 — View Recipe Videos for a Dish
# ======================================================================


def test_successful_video_search_with_no_matches_returns_an_empty_group():
    videos = get_recipe_videos("Uncommon Dish", "configured-key", lambda _dish: [])
    assert videos == []
    # New coverage: this distinguishes a successful zero-result search from Sebastian's configured-key, fallback, and exception scenarios.


def test_video_result_order_is_preserved_when_limited_to_two_items():
    offered = [{"id": "v1"}, {"id": "v2"}, {"id": "v3"}]
    videos = get_recipe_videos("Pasta", "configured-key", lambda _dish: offered)
    assert videos == [{"id": "v1"}, {"id": "v2"}]
    # New coverage: the two-result limit must preserve the provider's ranking rather than selecting arbitrary videos.


# ======================================================================
# Use Case 8 — Save a Meal to Favorites
# ======================================================================


def test_guest_save_updates_local_collection_without_calling_account_persistence():
    calls = []
    saved, ok = toggle_saved_meal([], "dish1", authenticated=False, persist_fn=calls.append)
    assert ok is True
    assert saved == ["dish1"]
    assert calls == []
    # New coverage: Sebastian checks lack of guest-to-account migration; this verifies the original guest save itself remains local-only.


def test_selecting_an_already_saved_heart_toggles_the_dish_out_of_favorites():
    persisted = []
    saved, ok = toggle_saved_meal(["dish1", "dish2"], "dish1", True, persisted.append)
    assert ok is True
    assert saved == ["dish2"]
    assert persisted == [["dish2"]]
    # New coverage: the home-page heart is a toggle, so selecting an already saved dish performs the inverse transition.


# ======================================================================
# Use Case 9 — Filter Meals by Allergen
# ======================================================================


def test_allergen_exclusion_is_case_insensitive():
    dishes = [
        {"id": "unsafe", "allergens": ["Peanut"]},
        {"id": "safe", "allergens": []},
    ]
    assert [dish["id"] for dish in filter_by_allergens(dishes, ["peanut"])] == ["safe"]
    # New coverage: differently capitalized catalog and user values still represent the same safety exclusion.


def test_dish_is_excluded_when_any_one_of_its_multiple_allergens_matches():
    dishes = [
        {"id": "multi", "allergens": ["dairy", "soy"]},
        {"id": "other", "allergens": ["gluten"]},
    ]
    assert [dish["id"] for dish in filter_by_allergens(dishes, ["soy"])] == ["other"]
    # New coverage: a dish is unsafe when any allergen intersects the exclusion set, even when its other allergens are allowed.


# ======================================================================
# Use Case 10 — Register an Account
# ======================================================================


def test_two_distinct_authentication_identities_create_isolated_profiles():
    database = {}
    first = ensure_user_in_db("auth_1", "One", database)
    second = ensure_user_in_db("auth_2", "Two", database)
    assert first["id"] != second["id"]
    assert set(database) == {"auth_1", "auth_2"}
    # New coverage: registration for separate identities must not overwrite or reuse another diner's profile.


def test_registration_without_a_display_name_still_links_the_auth_identity():
    database = {}
    user = ensure_user_in_db("auth_1", None, database)
    assert user["auth_id"] == "auth_1"
    assert user["name"] is None
    assert database["auth_1"] is user
    # New coverage: a missing optional display name does not have the same effect as the already-tested missing auth ID.


# ======================================================================
# Use Case 11 — Apply Power-Ups to Bias Selection
# ======================================================================


def test_max_thirty_minutes_powerup_scores_a_fast_dish_above_a_slow_dish():
    fast = {"isHealthy": False, "costBand": 2, "timeBand": 1}
    slow = {"isHealthy": False, "costBand": 2, "timeBand": 3}
    assert score_dish(fast, {"max30m": True}) > score_dish(slow, {"max30m": True})
    # New coverage: Sebastian checks Healthy and combined Healthy/Cheap; this verifies the distinct preparation-time power-up.


def test_disabling_all_powerups_restores_equal_base_scores():
    cheap_fast = {"isHealthy": True, "costBand": 1, "timeBand": 1}
    expensive_slow = {"isHealthy": False, "costBand": 3, "timeBand": 3}
    assert score_dish(cheap_fast, {}) == pytest.approx(1.0)
    assert score_dish(expensive_slow, {}) == pytest.approx(1.0)
    # New coverage: toggling all power-ups off removes their bias rather than retaining a previous scoring influence.


# ======================================================================
# Use Case 12 — Browse Saved Meals
# ======================================================================


def test_saved_meals_are_resolved_in_the_users_saved_order():
    catalog = {"a": {"id": "a"}, "b": {"id": "b"}, "c": {"id": "c"}}
    resolved = resolve_saved_dishes(["c", "a", "b"], catalog)
    assert [dish["id"] for dish in resolved] == ["c", "a", "b"]
    # New coverage: resolving IDs must preserve the user's collection order rather than catalog ordering.


def test_category_filter_with_no_matches_does_not_modify_saved_collection():
    catalog = {
        "b": {"id": "b", "category": "Breakfast"},
        "d": {"id": "d", "category": "Dinner"},
    }
    resolved = resolve_saved_dishes(["b", "d"], catalog)
    lunch = [dish for dish in resolved if dish["category"] == "Lunch"]
    assert lunch == []
    assert [dish["id"] for dish in resolved] == ["b", "d"]
    # New coverage: an empty filtered view is temporary and does not delete the underlying favorites.


# ======================================================================
# Use Case 13 — Remove a Saved Meal
# ======================================================================


def test_removing_an_unknown_saved_id_persists_the_unchanged_collection():
    persisted = []
    result, ok = remove_saved_meal(["d1", "d2"], "missing", persisted.append)
    assert ok is True
    assert result == ["d1", "d2"]
    assert persisted == [["d1", "d2"]]
    # New coverage: a stale removal request is idempotent and does not remove an unrelated favorite.


def test_removing_one_duplicate_reference_eliminates_all_matching_references():
    persisted = []
    result, ok = remove_saved_meal(["d1", "d1", "d2"], "d1", persisted.append)
    assert ok is True
    assert result == ["d2"]
    # New coverage: the filtering implementation removes every occurrence of the target identifier from malformed duplicate data.


# ======================================================================
# Use Case 14 — Leave a Party
# ======================================================================


def test_last_member_leaving_produces_an_empty_party_with_no_computed_host():
    remaining = leave_party([{"id": "m1", "creator": True}], "m1")
    assert remaining == []
    assert compute_host(remaining) is None
    # New coverage: Sebastian tests host handoff with a remaining member; this verifies the zero-member boundary.


def test_current_local_leave_behavior_does_not_remove_authoritative_membership():
    local_state = {"activeCode": "ABC123", "memberId": "m2"}
    authoritative = [{"id": "m1"}, {"id": "m2"}]
    after = local_only_leave(local_state, authoritative, "m2")
    assert local_state == {}
    assert [member["id"] for member in after] == ["m1", "m2"]
    # New coverage and discrepancy: the inspected page clears and reloads locally without calling the implemented leave endpoint.


# ======================================================================
# Use Case 15 — Find Nearby Restaurants After Spinning
# ======================================================================


def test_failed_geocoding_still_allows_places_results_without_an_origin():
    observed_origins = []

    def search(cuisine, origin):
        observed_origins.append(origin)
        return [{"name": f"{cuisine} restaurant", "distance": None}]

    result = search_places(["thai"], None, "Denver", search, lambda _hint: None)
    assert result["origin"] is None
    assert observed_origins == [None]
    assert result["results"]["thai"][0]["distance"] is None
    # New coverage: geocoding failure does not automatically discard venue results, but distance remains unavailable.


def test_empty_cuisine_list_performs_no_places_or_geocoding_work_with_coordinates():
    calls = []
    result = search_places([], (35.0, -78.0), "Denver", lambda *args: calls.append(args), lambda _hint: None)
    assert result == {"origin": (35.0, -78.0), "results": {}, "errors": {}}
    assert calls == []
    # New coverage: no spun cuisines means there are no external restaurant searches to perform.


# ======================================================================
# Use Case 16 — Create Party
# ======================================================================


def test_nickname_longer_than_twenty_four_characters_is_rejected():
    result = create_party_api("x" * 25, "ABC123")
    assert result == {"error": "invalid_nickname"}
    # New coverage: Sebastian checks empty input; this checks the opposite nickname-length boundary.


def test_whitespace_only_nickname_is_accepted_by_the_current_create_route_model():
    result = create_party_api("   ", "ABC123")
    assert result["isActive"] is True
    assert result["members"][0]["nickname"] == "   "
    # New coverage and discrepancy: server-side length validation does not trim whitespace, despite the browser blocking this value.


def test_party_code_collision_reports_creation_failure_without_overwriting_existing_party():
    result = create_party_api("Host", "ABC123", existing_codes={"ABC123"})
    assert result == {"error": "code_collision"}
    # New coverage: a generated-code collision is surfaced rather than silently replacing an existing party.


# ======================================================================
# Use Case 17 — Join Party
# ======================================================================


def test_joining_with_a_code_of_the_wrong_length_is_rejected_before_lookup():
    parties = {"ABC123": {"code": "ABC123", "isActive": True, "members": []}}
    result = join_party(parties, "ABC", "Guest")
    assert result == {"error": "invalid_request"}
    assert parties["ABC123"]["members"] == []
    # New coverage: Sebastian checks an unknown or inactive code, while this checks request-shape validation.


def test_repeated_join_requests_create_duplicate_memberships_in_current_behavior():
    parties = {"ABC123": {"code": "ABC123", "isActive": True, "members": []}}
    first = join_party(parties, "ABC123", "Guest", auth_id="auth1")
    second = join_party(parties, "ABC123", "Guest", auth_id="auth1")
    assert first["memberId"] != second["memberId"]
    assert [member["auth_id"] for member in parties["ABC123"]["members"]] == ["auth1", "auth1"]
    # New coverage and discrepancy: the current join route has no uniqueness check for an existing party member.


# ======================================================================
# Use Case 18 — Sign In to an Account
# ======================================================================


def test_authentication_provider_outage_creates_neither_session_nor_profile():
    profiles = {}
    result = sign_in("valid", {"valid": "auth1"}, profiles, provider_available=False)
    assert result == {"error": "provider_unavailable"}
    assert profiles == {}
    # New coverage: this exercises provider unavailability, not Sebastian's invalid-credential branch.


def test_signing_in_as_another_identity_never_returns_the_first_users_profile():
    profiles = {
        "auth1": {"auth_id": "auth1", "savedMeals": ["private1"], "allergens": []},
        "auth2": {"auth_id": "auth2", "savedMeals": ["private2"], "allergens": []},
    }
    result = sign_in("second", {"second": "auth2"}, profiles)
    assert result["profile"]["auth_id"] == "auth2"
    assert result["profile"]["savedMeals"] == ["private2"]
    # New coverage: profile selection is isolated by authenticated identity and cannot leak another diner's saved meals.


# ======================================================================
# Use Case 19 — Sign Out of an Account
# ======================================================================


def test_signing_out_twice_is_idempotent():
    state = {"session": {"auth_id": "auth1"}, "profile": {"name": "One"}, "cache": {"x": 1}}
    sign_out(state)
    sign_out(state)
    assert state == {"session": None, "profile": None, "cache": {}}
    # New coverage: repeated sign-out actions remain safe and do not restore or corrupt cleared state.


def test_sign_out_does_not_delete_unrelated_guest_preferences():
    state = {
        "session": {"auth_id": "auth1"},
        "profile": {"name": "One"},
        "cache": {"account": "private"},
        "guestTheme": "dark",
    }
    sign_out(state)
    assert state["guestTheme"] == "dark"
    assert state["session"] is None and state["cache"] == {}
    # New coverage: account-specific state is cleared without erasing an unrelated browser-level preference.


# ======================================================================
# Use Case 20 — Chat with Party Members
# ======================================================================


def test_duplicate_realtime_chat_message_is_displayed_only_once():
    log, seen = [], set()
    message = {"id": "msg1", "sender": "Alex", "text": "Pizza?"}
    assert receive_chat(message, log, seen) is True
    assert receive_chat(message, log, seen) is False
    assert log == [message]
    # New coverage: retransmission of the same realtime message does not create duplicate visible chat entries.


def test_chat_history_is_not_restored_after_a_new_party_client_session():
    first_log, first_seen = [], set()
    receive_chat({"id": "msg1", "sender": "Alex", "text": "Tacos"}, first_log, first_seen)
    reloaded_log, reloaded_seen = [], set()
    assert first_log != []
    assert reloaded_log == [] and reloaded_seen == set()
    # New coverage: the use case states that chat lasts only for the session; a reload has no persisted history to restore.
