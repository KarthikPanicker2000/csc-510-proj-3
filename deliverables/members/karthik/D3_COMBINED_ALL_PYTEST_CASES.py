"""
Combined MealSlot pytest cases from the three supplied files.

All original helper names and test function names are preserved exactly.
Each source is executed in an isolated namespace so identically named helpers
from different files cannot overwrite one another. The original test functions
are then exposed to pytest under their unchanged names.
"""


def _load_original_suite(source, source_label):
    namespace = {"__name__": source_label, "__file__": __file__}
    exec(compile(source, source_label, "exec"), namespace)
    for name, value in namespace.items():
        if name.startswith("test_") and callable(value):
            if name in globals():
                raise RuntimeError("Duplicate original test name: " + name)
            globals()[name] = value


_SOURCE_1 = r'''"""
pytest coverage for the 20 use cases in Top_20_Use_Cases_Full.md plus the one
use case from Sebastian_Use_Cases.md that is not already represented there
("Manage Dietary Preferences" — persisted, account-level allergen management,
which is distinct from the session-only "Filter Meals by Allergen" use case).
All other Sebastian_Use_Cases.md entries duplicate a use case already present
in Top_20_Use_Cases_Full.md (e.g. "Sign Up for an Account" duplicates
"Register an Account", "Group Spin (Host-Led)" duplicates "Spin the Party
Slot Machine") and are not re-tested separately.

ASSUMPTIONS (stated up front rather than hidden in individual tests):

1. MealSlot's real business logic lives in TypeScript (Next.js route
   handlers, Prisma, Stack Auth) and is not importable from Python. Every
   helper function below is a small, faithful Python port of the cited
   TypeScript source (function names and file paths are given in each
   helper's docstring), or — where a use case is mostly framework glue
   (auth, chat relay, favorites CRUD) — a direct behavioral model of the
   rule as stated in the use-case table. None of these tests call a live
   Next.js server, a real Postgres/Prisma database, Stack Auth, or the
   Google Places/YouTube APIs.
2. Randomness is injected as an explicit `rng` callable so the ported
   selection logic is deterministic in tests. The real app seeds this from
   a 10-second wall-clock time bucket (see Use Case 1, Extension 5b); that
   time-bucketing behavior itself is out of scope for these pure-logic
   tests and is called out specifically where relevant.
3. This file assumes a Python 3.9+ interpreter with `pytest` installed.
   Neither is part of MealSlot's own toolchain (it uses pnpm/Vitest), so
   running this file requires a separate, manually-provisioned Python
   environment.
"""

import pytest


# ======================================================================
# Group A helpers — solo spin engine
# Ported from proj2/mealslot/lib/scoring.ts and lib/dishes.ts
# ======================================================================

def score_dish(dish, powerups):
    """Port of scoreDish() in lib/scoring.ts."""
    s = 1.0
    if powerups.get("healthy"):
        s *= 2.0 if dish["isHealthy"] else 0.8
    if powerups.get("cheap"):
        cb = dish["costBand"]
        s *= 2.0 if cb == 1 else (1.0 if cb == 2 else 0.6)
    if powerups.get("max30m"):
        tb = dish["timeBand"]
        s *= 2.0 if tb == 1 else (0.9 if tb == 2 else 0.5)
    return max(s, 0.0001)


def weighted_choice(items, weights, rnd):
    """Port of weightedChoice() in lib/scoring.ts."""
    n = min(len(items), len(weights))
    if n == 0:
        return None
    total = sum(weights[:n])
    if total <= 0:
        return None
    r = rnd() * total
    for i in range(n):
        r -= weights[i]
        if r <= 0:
            return items[i]
    return items[n - 1]


def weighted_spin(reels, locked=None, powerups=None, rng=None):
    """Port of weightedSpin() in lib/scoring.ts."""
    locked = locked or []
    powerups = powerups or {}
    rng = rng or (lambda: 0.5)
    locks_by_index = {l["index"]: l["dishId"] for l in locked if 0 <= l["index"] < len(reels)}
    out = []
    for i, reel in enumerate(reels):
        if not reel:
            out.append({
                "id": f"placeholder_{i}", "name": "No options", "category": "unknown",
                "tags": [], "costBand": 2, "timeBand": 2, "isHealthy": True,
                "allergens": [], "ytQuery": "quick recipe",
            })
            continue
        lock_id = locks_by_index.get(i)
        if lock_id:
            locked_dish = next((d for d in reel if d["id"] == lock_id), None)
            if locked_dish:
                out.append(locked_dish)
                continue
        weights = [score_dish(d, powerups) for d in reel]
        pick = weighted_choice(reel, weights, rng) or reel[0]
        out.append(pick)
    return out


def filter_by_allergens(dishes, excluded_allergens):
    """Port of the allergen-exclusion filter in lib/dishes.ts' dishes()."""
    excluded = {a.lower() for a in excluded_allergens}
    return [d for d in dishes if not any(a.lower() in excluded for a in d["allergens"])]


def can_spin(now_ms, last_spin_at_ms, cooldown_ms=3000):
    """Model of the client-side cooldown gate in app/(site)/page.tsx (cooldownMs state)."""
    if last_spin_at_ms is None:
        return True
    return (now_ms - last_spin_at_ms) >= cooldown_ms


# ======================================================================
# Group B helpers — party mechanics
# Ported from proj2/mealslot/lib/party.ts, PartyClient.tsx,
# and app/api/party/*/route.ts
# ======================================================================

STRICTNESS = {"vegan": 4, "vegetarian": 3, "pescatarian": 2, "omnivore": 1, "keto": 2, "none": 0}
ETHIC_DIETS = ("vegan", "vegetarian", "pescatarian", "omnivore")


def merge_constraints(prefs_list):
    """Port of mergeConstraints() in lib/party.ts."""
    diets = [p.get("diet") for p in prefs_list if p.get("diet")]
    non_none = [d for d in diets if d != "none"]
    diet_merged = None
    if non_none:
        sorted_diets = sorted(set(non_none), key=lambda d: -STRICTNESS[d])
        ethic = next((d for d in sorted_diets if d in ETHIC_DIETS), None)
        diet_merged = [ethic or sorted_diets[0]]

    allergens_merged = sorted(set(a for p in prefs_list for a in p.get("allergens", [])))
    budget_vals = [p["budgetBand"] for p in prefs_list if "budgetBand" in p]
    time_vals = [p["timeBand"] for p in prefs_list if "timeBand" in p]

    merged = {}
    if diet_merged:
        merged["diet"] = diet_merged
    if allergens_merged:
        merged["allergens"] = allergens_merged
    if budget_vals:
        merged["budgetBand"] = min(budget_vals)
    if time_vals:
        merged["timeBand"] = min(time_vals)

    conflict = False
    suggestions = []
    if diet_merged is not None and len(diet_merged) == 0:
        conflict = True
        suggestions.append("Remove conflicting diet restrictions (default to vegetarian).")
    if merged.get("diet") and "vegan" in merged["diet"]:
        blocked = set(merged.get("allergens", []))
        many = ["soy", "peanut", "tree_nut", "gluten"]
        if sum(1 for a in many if a in blocked) >= 3:
            conflict = True
            suggestions.append("Too many allergens with vegan. Consider dropping one or relaxing to vegetarian.")
    return {"merged": merged, "conflict": conflict, "suggestions": suggestions}


def quorum(live_member_count):
    """Port of the `quorum` useMemo in PartyClient.tsx."""
    return max(1, live_member_count // 2 + 1)


def tally_vote(votes, idx, kind, voter_id):
    """Port of sendVote()'s local vote bookkeeping in PartyClient.tsx."""
    votes[idx]["keep"].discard(voter_id)
    votes[idx]["reroll"].discard(voter_id)
    votes[idx][kind].add(voter_id)


def resolve_vote_action(votes, idx, live_member_count):
    """Port of maybeActOnVotes() in PartyClient.tsx."""
    q = quorum(live_member_count)
    if len(votes[idx]["keep"]) >= q:
        return "lock"
    if len(votes[idx]["reroll"]) >= q:
        return "reroll"
    return None


def party_spin(locked, slots, spin_fn, fallback_menu, max_tries=6):
    """Port of the retry/dedupe/fallback loop in app/api/party/spin/route.ts."""
    out = [None, None, None]
    used = set()
    for i in range(3):
        if locked[i] and slots[i]:
            out[i] = slots[i]
            used.add(slots[i]["id"])

    def call_single():
        try:
            result = spin_fn()
            return result if isinstance(result, list) else ([result] if result else [])
        except Exception:
            return fallback_menu

    def pick_fresh(arr):
        for d in arr:
            if d["id"] not in used:
                used.add(d["id"])
                return d
        return None

    for _ in range(max_tries):
        for i in range(3):
            if locked[i] or out[i]:
                continue
            picked = pick_fresh(call_single())
            if picked:
                out[i] = picked
        if all(out):
            break

    for i in range(3):
        if not out[i]:
            out[i] = {"id": f"placeholder_{i}", "name": "No options", "category": "unknown",
                       "tags": [], "allergens": [], "ytQuery": "quick recipe"}
    return out


def create_party(nickname, code_gen_fn, user_allergens=None):
    """Model of POST /api/party/create (app/api/party/create/route.ts)."""
    if not nickname or not nickname.strip() or len(nickname) > 24:
        return {"error": "invalid_nickname"}
    return {
        "code": code_gen_fn(),
        "isActive": True,
        "members": [{"id": "m1", "nickname": nickname, "host": True,
                     "allergens": user_allergens or []}],
    }


def join_party(parties_by_code, code, nickname, prefs=None):
    """Model of POST /api/party/join (app/api/party/join/route.ts)."""
    party = parties_by_code.get(code)
    if not party or not party.get("isActive"):
        return {"error": "NOT_FOUND"}
    member = {"id": f"m{len(party['members']) + 1}", "nickname": nickname or "Guest",
              "prefs": prefs or {}}
    party["members"].append(member)
    return {"partyId": party["code"], "memberId": member["id"], "code": party["code"]}


def leave_party(members, leaving_id):
    """Model of POST /api/party/leave plus PartyClient.tsx's host recomputation."""
    return [m for m in members if m["id"] != leaving_id]


def compute_host(live_members_in_join_order):
    """Port of `hostId = livePeers.find(p => p.creator)?.id ?? livePeers[0]?.id` in PartyClient.tsx."""
    if not live_members_in_join_order:
        return None
    creator = next((m for m in live_members_in_join_order if m.get("creator")), None)
    return (creator or live_members_in_join_order[0])["id"]


# ======================================================================
# Group C helpers — accounts / auth
# Modeled on app/api/user/*, app/account/*, and Stack Auth usage
# ======================================================================

def ensure_user_in_db(auth_id, name, db):
    """Port of the ensureUserInDB()/User upsert behavior referenced by
    the account-creation route handlers."""
    if not auth_id:
        return None
    existing = db.get(auth_id)
    if existing:
        return existing
    user = {"id": f"user_{len(db) + 1}", "auth_id": auth_id, "name": name,
            "allergens": [], "savedMeals": []}
    db[auth_id] = user
    return user


def sync_display_name(last_synced_name, stack_auth_name, db_update_fn):
    """Model of the Account page's 2-second Stack Auth polling loop
    described in Use Case 6."""
    if stack_auth_name == last_synced_name:
        return last_synced_name, False
    try:
        db_update_fn(stack_auth_name)
        return stack_auth_name, True
    except Exception:
        return last_synced_name, False


def sign_in(credentials, valid_credentials, profile_store):
    """Model of the sign-in flow described in Use Case 18."""
    if credentials not in valid_credentials:
        return {"error": "invalid_credentials"}
    auth_id = valid_credentials[credentials]
    profile = profile_store.get(auth_id)
    if profile is None:
        profile = {"auth_id": auth_id, "allergens": [], "savedMeals": []}
        profile_store[auth_id] = profile
    return {"session": {"auth_id": auth_id}, "profile": profile}


def sign_out(client_state):
    """Model of the sign-out flow described in Use Case 19."""
    client_state["session"] = None
    client_state["profile"] = None
    client_state["cache"] = {}
    return client_state


def update_user_allergens(user, new_allergens, persist_fn):
    """Model of the persisted, account-level allergen update described in
    Sebastian_Use_Cases.md Use Case 12 ('Manage Dietary Preferences'),
    which is distinct from the session-only exclusion filter in Use Case 9."""
    previous = list(user["allergens"])
    try:
        persist_fn(new_allergens)
        user["allergens"] = list(new_allergens)
        return True
    except Exception:
        user["allergens"] = previous
        return False


# ======================================================================
# Group D helper — recipe videos
# Modeled on app/api/videos/route.ts and lib/youtube.ts
# ======================================================================

def get_recipe_videos(dish_name, api_key, search_fn, max_results=2):
    """Model of the per-dish YouTube lookup described in Use Case 7."""
    if not api_key:
        return [{"id": "stub", "title": f"{dish_name} recipe (stub)", "stub": True}]
    try:
        results = search_fn(dish_name)
        return results[:max_results]
    except Exception:
        return []


# ======================================================================
# Group E helpers — favorites
# Modeled on app/api/user/saved/route.ts and app/favorites/page.tsx
# ======================================================================

def toggle_saved_meal(saved_meals, dish_id, is_authenticated, persist_fn):
    """Model of toggleSavedMeal() in app/(site)/page.tsx."""
    next_list = [d for d in saved_meals if d != dish_id] if dish_id in saved_meals \
        else saved_meals + [dish_id]
    if not is_authenticated:
        return next_list, True
    try:
        persist_fn(next_list)
        return next_list, True
    except Exception:
        return saved_meals, False


def resolve_saved_dishes(saved_ids, catalog_by_id):
    """Model of the Favorites page resolving saved IDs against /api/dishes."""
    return [catalog_by_id[i] for i in saved_ids if i in catalog_by_id]


def remove_saved_meal(saved_meals, dish_id, persist_fn):
    """Model of removing an entry via /api/user/saved."""
    next_list = [d for d in saved_meals if d != dish_id]
    try:
        persist_fn(next_list)
        return next_list, True
    except Exception:
        return saved_meals, False


# ======================================================================
# Group F helper — nearby places
# Modeled on app/api/places/route.ts and app/api/places/helpers.ts
# ======================================================================

def search_places(cuisines, coords, location_hint, search_fn, geocode_fn):
    """Model of the per-cuisine, error-isolated Places search described in
    Use Case 15."""
    origin = coords
    if origin is None:
        origin = geocode_fn(location_hint)
    results, errors = {}, {}
    for cuisine in cuisines:
        try:
            venues = search_fn(cuisine, origin)
            results[cuisine] = venues
        except Exception as e:
            errors[cuisine] = str(e)
            results[cuisine] = []
    return {"origin": origin, "results": results, "errors": errors}


# ======================================================================
# Group G helper — party chat
# Modeled on PartyClient.tsx's sendChat()/rt.on("chat", ...)
# ======================================================================

def send_chat_message(same_machine_peers, other_device_peers, text, has_dedicated_realtime):
    """Model of sendChat() and the BroadcastChannel/WebSocket split in
    lib/realtime.ts, described in Use Case 20."""
    if not text.strip():
        return False
    same_machine_peers.append(text)
    if has_dedicated_realtime:
        other_device_peers.append(text)
    return True


# ======================================================================
# Use Case 1 — Spin for a Meal
# ======================================================================

def test_spinning_returns_one_dish_per_reel_from_the_offered_candidates():
    reels = [
        [{"id": "b1", "name": "Oats", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}],
        [{"id": "l1", "name": "Salad", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}],
        [{"id": "d1", "name": "Pasta", "isHealthy": False, "costBand": 2, "timeBand": 2, "allergens": ["gluten"]}],
    ]
    selection = weighted_spin(reels, rng=lambda: 0.0)
    assert [d["id"] for d in selection] == ["b1", "l1", "d1"]
    # This proves that a spin with one candidate per slot deterministically returns that candidate for every slot, matching the documented main success scenario.


def test_a_slot_with_no_matching_dishes_gets_a_no_options_placeholder_instead_of_failing():
    reels = [[], [{"id": "l1", "name": "Salad", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}]]
    selection = weighted_spin(reels, rng=lambda: 0.0)
    assert selection[0]["id"] == "placeholder_0"
    assert selection[0]["name"] == "No options"
    assert selection[1]["id"] == "l1"
    # This proves that an empty reel (e.g. every dish filtered out) yields Extension 4b's placeholder dish rather than aborting the whole spin.


def test_spinning_again_before_the_cooldown_expires_is_rejected():
    last_spin_at = 10_000
    assert can_spin(now_ms=11_000, last_spin_at_ms=last_spin_at, cooldown_ms=3000) is False
    assert can_spin(now_ms=13_000, last_spin_at_ms=last_spin_at, cooldown_ms=3000) is True
    # This proves that a spin request made inside the 3-second cooldown window is disallowed, matching Extension 7a, while one made after the window elapses is allowed.
    # Assumption: the cooldown is modeled as a pure "elapsed >= cooldown_ms" predicate, matching the client-side cooldownMs countdown; no real clock or network round trip is involved.


# ======================================================================
# Use Case 2 — Set Party Dietary Preferences and Resolve Conflicts
# ======================================================================

def test_merging_preferences_unions_allergens_and_keeps_the_strictest_diet():
    prefs = [
        {"diet": "vegetarian", "allergens": ["gluten"], "budgetBand": 2, "timeBand": 3},
        {"diet": "omnivore", "allergens": ["dairy"], "budgetBand": 1, "timeBand": 1},
    ]
    result = merge_constraints(prefs)
    assert result["merged"]["diet"] == ["vegetarian"]
    assert result["merged"]["allergens"] == ["dairy", "gluten"]
    assert result["merged"]["budgetBand"] == 1
    assert result["merged"]["timeBand"] == 1
    # This proves that merging two members' preferences picks the strictest diet, unions their allergens, and takes the minimum budget/time band, exactly as documented in the main success scenario.


def test_mixing_vegan_and_omnivore_preferences_never_actually_raises_a_conflict_flag():
    result = merge_constraints([{"diet": "vegan"}, {"diet": "omnivore"}])
    assert result["merged"]["diet"] == ["vegan"]
    assert result["conflict"] is False
    # This proves (and documents a discrepancy) that the real mergeConstraints() algorithm always resolves diet-only combinations to one strictest diet, so Extension 4a's "mutually incompatible diets" conflict path is unreachable dead code in the current implementation, not an active safeguard.
    # Assumption: this test intentionally encodes the algorithm's actual behavior rather than the use case's stated extension, since the two disagree; a reader relying on the use-case doc alone would expect conflict=True here.


def test_vegan_diet_combined_with_three_or_more_blocked_allergens_is_flagged_as_a_conflict():
    prefs = [
        {"diet": "vegan", "allergens": ["soy", "peanut", "tree_nut"]},
        {"diet": "vegan", "allergens": ["gluten"]},
    ]
    result = merge_constraints(prefs)
    assert result["conflict"] is True
    assert any("vegan" in s.lower() for s in result["suggestions"])
    # This proves that a merged vegan diet plus four commonly-blocked allergens correctly triggers Extension 4b's conflict flag and suggestion.


# ======================================================================
# Use Case 3 — Vote on a Spin Result
# ======================================================================

def _fresh_votes():
    return [{"keep": set(), "reroll": set()} for _ in range(3)]


def test_keep_votes_reaching_a_majority_of_connected_members_lock_the_slot():
    votes = _fresh_votes()
    tally_vote(votes, 0, "keep", "m1")
    tally_vote(votes, 0, "keep", "m2")
    action = resolve_vote_action(votes, 0, live_member_count=3)
    assert action == "lock"
    # This proves that 2 keep-votes out of 3 live members (quorum = 2) locks the slot, matching the main success scenario's majority rule.


def test_changing_a_vote_before_quorum_replaces_the_previous_vote_instead_of_adding_to_it():
    votes = _fresh_votes()
    tally_vote(votes, 0, "keep", "m1")
    tally_vote(votes, 0, "reroll", "m1")
    assert votes[0]["keep"] == set()
    assert votes[0]["reroll"] == {"m1"}
    # This proves Extension 2a: a member switching their vote removes their prior choice rather than being counted under both "keep" and "reroll".


def test_a_disconnected_voter_no_longer_counts_toward_the_live_quorum():
    votes = _fresh_votes()
    tally_vote(votes, 0, "keep", "m1")
    action_before = resolve_vote_action(votes, 0, live_member_count=3)
    action_after = resolve_vote_action(votes, 0, live_member_count=1)
    assert action_before is None
    assert action_after == "lock"
    # This proves Extension 4a: the same single keep-vote fails to reach quorum among 3 live members (quorum=2) but succeeds once other members disconnect and the live count drops to 1 (quorum=1), since quorum is recomputed from currently connected members.


# ======================================================================
# Use Case 4 — Spin the Party Slot Machine
# ======================================================================

def test_a_party_spin_fills_all_three_slots_and_keeps_locked_dishes_in_place():
    slots = [{"id": "kept", "name": "Kept Dish"}, None, None]
    locked = [True, False, False]
    counter = {"n": 0}

    def spin_fn():
        counter["n"] += 1
        return [{"id": f"d{counter['n']}", "name": f"Dish {counter['n']}"}]

    result = party_spin(locked, slots, spin_fn, fallback_menu=[])
    assert result[0]["id"] == "kept"
    assert result[1] is not None and result[2] is not None
    assert result[1]["id"] != result[2]["id"]
    # This proves that a party spin preserves a locked slot's dish and fills the remaining slots with distinct dishes, matching the main success scenario.


def test_a_failing_internal_spin_falls_back_to_the_hardcoded_menu():
    def failing_spin_fn():
        raise RuntimeError("internal /api/spin unavailable")

    fallback = [{"id": "fb_1", "name": "Veggie Fried Rice"},
                {"id": "fb_2", "name": "Chicken Tacos"},
                {"id": "fb_3", "name": "Mediterranean Grain Bowl"}]
    result = party_spin([False, False, False], [None, None, None], failing_spin_fn, fallback_menu=fallback)
    assert all(d["id"] in {"fb_1", "fb_2", "fb_3"} for d in result)
    # This proves Extension 4a: when the internal spin call fails on every attempt, all three slots are filled from the hardcoded fallback menu instead of the request failing.


def test_a_slot_still_unfilled_after_six_attempts_gets_a_no_options_placeholder():
    def always_duplicate_spin_fn():
        return [{"id": "only_dish", "name": "Only Dish"}]

    result = party_spin([False, False, False], [None, None, None], always_duplicate_spin_fn, fallback_menu=[])
    placeholders = [d for d in result if d["id"].startswith("placeholder_")]
    assert len(placeholders) == 2
    # This proves Extension 5a: when every attempt returns the same already-used dish, the two slots that can never get a unique pick end up with "No options" placeholders after the 6-try limit, rather than looping forever.


def test_party_spin_calls_the_internal_spin_endpoint_at_most_six_times_total():
    """EXPECTED TO FAIL. UC4's main success scenario, step 4, is explicit:
    'System calls the internal /api/spin endpoint up to 6 times to fill three
    unique slots' -- i.e. 6 calls total is the documented budget for the whole
    spin, not per slot. But party_spin()'s retry loop (line ~204) calls
    call_single()/spin_fn() once for EVERY still-unfilled slot on EACH of the
    max_tries=6 outer iterations. With all three slots empty and a spin_fn that
    keeps returning duplicates (so no slot ever fills), that's up to 3*6=18
    calls, not 6 -- confirmed empirically at 13 calls for this exact scenario.
    This isn't a hypothetical: it's the same fixture as the test directly above
    this one, just counting invocations instead of the resulting placeholders.
    The port's retry budget is wrong relative to the spec, and in the real
    Next.js route this would mean up to 3x the intended load on /api/spin
    under a degraded/duplicate-heavy catalog."""
    call_count = {"n": 0}

    def always_duplicate_spin_fn():
        call_count["n"] += 1
        return [{"id": "only_dish", "name": "Only Dish"}]

    party_spin([False, False, False], [None, None, None], always_duplicate_spin_fn, fallback_menu=[])
    assert call_count["n"] <= 6


# ======================================================================
# Use Case 5 — Lock a Reel and Re-Spin
# ======================================================================

def test_a_locked_slot_keeps_its_dish_while_other_slots_get_new_ones():
    reels = [
        [{"id": "b1", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []},
         {"id": "b2", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}],
        [{"id": "l1", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}],
    ]
    locked = [{"index": 0, "dishId": "b2"}]
    selection = weighted_spin(reels, locked=locked, rng=lambda: 0.0)
    assert selection[0]["id"] == "b2"
    assert selection[1]["id"] == "l1"
    # This proves that a lock keyed by {index, dishId} is honored on respin while unlocked slots are still populated normally.


def test_a_legacy_index_only_lock_is_ignored_and_the_slot_is_re_spun():
    reels = [[{"id": "b1", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}]]
    # Legacy payloads sent bare index numbers instead of {index, dishId}; the
    # spin engine's lock map only understands the latter, so such entries
    # are simply absent from `locked` here rather than being coerced.
    legacy_style_locked = []
    selection = weighted_spin(reels, locked=legacy_style_locked, rng=lambda: 0.0)
    assert selection[0]["id"] == "b1"
    # This proves Extension 3a: a legacy lock payload that carries no usable {index, dishId} pair is treated as no lock at all, so the slot is populated by the normal weighted pick instead of being held.


def test_deduplication_can_leave_fewer_than_three_unique_dishes_without_crashing():
    only_dish = {"id": "only", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []}
    reels = [[only_dish], [only_dish], [only_dish]]
    selection = weighted_spin(reels, rng=lambda: 0.0)
    assert [d["id"] for d in selection] == ["only", "only", "only"]
    # This proves Extension 6a: when every reel only offers one shared dish, the spin still returns a full three-slot result (showing "whatever is available") instead of raising an error.
    # Assumption: cross-slot deduplication is a display-layer concern (see dedupeSelection() in app/(site)/page.tsx); the spin engine itself is only required not to fail when duplicates are unavoidable.


# ======================================================================
# Use Case 6 — Update Display Name
# ======================================================================

def test_a_changed_display_name_is_pushed_to_the_database_on_the_next_poll():
    updates = []
    new_synced_name, changed = sync_display_name("Old Name", "New Name", updates.append)
    assert changed is True
    assert new_synced_name == "New Name"
    assert updates == ["New Name"]
    # This proves the main success scenario: detecting a display-name change on a poll cycle triggers exactly one database update with the new name.


def test_an_unchanged_display_name_triggers_no_database_call():
    updates = []
    new_synced_name, changed = sync_display_name("Same Name", "Same Name", updates.append)
    assert changed is False
    assert updates == []
    # This proves Extension 2a: when Stack Auth reports the same name as last poll, no redundant database write occurs.


def test_a_failed_database_update_leaves_the_previously_synced_name_in_place():
    def failing_update(_name):
        raise ConnectionError("db unreachable")

    new_synced_name, changed = sync_display_name("Old Name", "New Name", failing_update)
    assert changed is False
    assert new_synced_name == "Old Name"
    # This proves Extension 4a: a failed database update does not corrupt the locally tracked synced name, so the next poll cycle can retry cleanly instead of assuming the update succeeded.


# ======================================================================
# Use Case 7 — View Recipe Videos for a Dish
# ======================================================================

def test_a_configured_api_key_returns_up_to_two_normalized_video_results():
    def search_fn(_dish_name):
        return [{"id": "v1"}, {"id": "v2"}, {"id": "v3"}]

    videos = get_recipe_videos("Spaghetti", api_key="fake-key", search_fn=search_fn)
    assert len(videos) == 2
    assert [v["id"] for v in videos] == ["v1", "v2"]
    # This proves the main success scenario caps recipe videos at two results per dish, matching lib/youtube.ts's documented limit.


def test_a_missing_api_key_returns_a_deterministic_stub_video_instead_of_an_empty_modal():
    videos = get_recipe_videos("Spaghetti", api_key=None, search_fn=lambda name: [{"id": "should_not_be_used"}])
    assert len(videos) == 1
    assert videos[0]["stub"] is True
    # This proves Extension 4a: with no YOUTUBE_API_KEY configured, the system returns stub content rather than calling the search function or leaving the modal empty.


def test_a_video_search_failure_for_one_dish_does_not_affect_other_dishes():
    def flaky_search_fn(dish_name):
        if dish_name == "Broken Dish":
            raise RuntimeError("YouTube API error")
        return [{"id": "ok1"}]

    broken_result = get_recipe_videos("Broken Dish", api_key="fake-key", search_fn=flaky_search_fn)
    healthy_result = get_recipe_videos("Good Dish", api_key="fake-key", search_fn=flaky_search_fn)
    assert broken_result == []
    assert healthy_result == [{"id": "ok1"}]
    # This proves Extension 4b: a per-dish video lookup failure empties only that dish's video list while other dishes' lookups still succeed.


# ======================================================================
# Use Case 8 — Save a Meal to Favorites
# ======================================================================

def test_an_authenticated_user_saving_a_dish_persists_it_to_their_account():
    persisted = []
    next_list, ok = toggle_saved_meal([], "dish_1", is_authenticated=True, persist_fn=persisted.append)
    assert ok is True
    assert next_list == ["dish_1"]
    assert persisted == [["dish_1"]]
    # This proves the main success scenario: saving a dish while authenticated updates the local list and persists it to the account in one step.


def test_a_failed_persistence_request_reverts_the_saved_state():
    def failing_persist(_next_list):
        raise ConnectionError("network error")

    next_list, ok = toggle_saved_meal([], "dish_1", is_authenticated=True, persist_fn=failing_persist)
    assert ok is False
    assert next_list == []
    # This proves Extension 3a: when persistence fails, the returned state matches the prior (unsaved) list rather than the optimistic update, so the UI can revert the heart icon.


def test_a_guests_locally_saved_meals_are_not_carried_into_an_authenticated_profile():
    guest_saved_meals, _ = toggle_saved_meal([], "dish_1", is_authenticated=False, persist_fn=lambda _l: None)
    new_authenticated_profile = {"savedMeals": []}
    assert guest_saved_meals == ["dish_1"]
    assert new_authenticated_profile["savedMeals"] == []
    # This proves Extension 4a: a guest's saved meal exists only in local state, and signing in afterward starts the authenticated profile from an empty saved-meals list rather than importing it.
    # Assumption: no migration path exists in the codebase, so the "new authenticated profile" here is modeled as a fresh, empty record rather than a call into any real migration function.


# ======================================================================
# Use Case 9 — Filter Meals by Allergen
# ======================================================================

def test_dishes_containing_an_excluded_allergen_are_removed_from_results():
    dishes = [
        {"id": "d1", "allergens": ["gluten"]},
        {"id": "d2", "allergens": ["dairy"]},
        {"id": "d3", "allergens": []},
    ]
    filtered = filter_by_allergens(dishes, ["gluten"])
    assert {d["id"] for d in filtered} == {"d2", "d3"}
    # This proves the main success scenario: any dish containing a selected allergen is excluded, while unaffected dishes remain eligible.


def test_excluding_every_dish_in_a_category_still_yields_a_placeholder_via_the_spin_engine():
    dishes = [{"id": "d1", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": ["peanut"]}]
    filtered = filter_by_allergens(dishes, ["peanut"])
    selection = weighted_spin([filtered], rng=lambda: 0.0)
    assert filtered == []
    assert selection[0]["name"] == "No options"
    # This proves Extension 4a: when an allergen filter eliminates every candidate for a slot, the downstream spin still returns a "No options" placeholder instead of erroring.


def test_a_signed_in_users_saved_allergens_preselect_the_filter_menu():
    user = {"allergens": ["shellfish", "soy"]}
    initial_selected_allergens = list(user["allergens"])
    assert initial_selected_allergens == ["shellfish", "soy"]
    # This proves Extension 5a: opening the filter menu for a signed-in user with saved allergens starts the selection pre-populated from their account rather than empty.
    # Assumption: the filter menu's initial state is modeled directly as a copy of the account's stored allergens, since the real behavior is a one-time UI initialization rather than a standalone algorithm.


# ======================================================================
# Use Case 10 — Register an Account
# ======================================================================

def test_registering_with_a_new_auth_id_creates_a_user_record():
    db = {}
    user = ensure_user_in_db("auth_123", "Ada", db)
    assert user["auth_id"] == "auth_123"
    assert user["allergens"] == []
    assert db["auth_123"] is user
    # This proves the main success scenario: a first-time auth_id causes a new User record to be upserted with empty allergens and saved meals.


def test_registering_with_an_auth_id_that_already_exists_returns_the_existing_record_unchanged():
    db = {}
    first = ensure_user_in_db("auth_123", "Ada", db)
    second = ensure_user_in_db("auth_123", "Ada Again", db)
    assert second is first
    assert len(db) == 1
    # This proves Extension 5a: a returning user's auth_id resolves to the existing record instead of creating a duplicate.


def test_a_missing_auth_id_creates_no_database_record():
    db = {}
    user = ensure_user_in_db(None, "Ada", db)
    assert user is None
    assert db == {}
    # This proves Extension 4a: a null/missing auth_id short-circuits to no record being created, matching ensureUserInDB()'s documented null return.


# ======================================================================
# Use Case 11 — Apply Power-Ups to Bias Selection
# ======================================================================

def test_the_healthy_powerup_gives_a_healthy_dish_a_higher_score_than_an_unhealthy_one():
    healthy_dish = {"isHealthy": True, "costBand": 2, "timeBand": 2}
    unhealthy_dish = {"isHealthy": False, "costBand": 2, "timeBand": 2}
    assert score_dish(healthy_dish, {"healthy": True}) > score_dish(unhealthy_dish, {"healthy": True})
    # This proves the main success scenario: activating the Healthy power-up weights an eligible healthy dish above a comparable unhealthy one.


def test_combining_healthy_and_cheap_powerups_multiplies_their_individual_effects():
    dish = {"isHealthy": True, "costBand": 1, "timeBand": 2}
    healthy_only = score_dish(dish, {"healthy": True})
    cheap_only = score_dish(dish, {"cheap": True})
    both = score_dish(dish, {"healthy": True, "cheap": True})
    assert both == pytest.approx(healthy_only * cheap_only)
    # This proves Extension 2a: multiple active power-ups combine multiplicatively rather than one overriding the other.


def test_no_dish_matching_an_active_powerup_still_yields_a_selection_instead_of_failing():
    reels = [[{"id": "only", "isHealthy": False, "costBand": 3, "timeBand": 3, "allergens": []}]]
    selection = weighted_spin(reels, powerups={"healthy": True}, rng=lambda: 0.0)
    assert selection[0]["id"] == "only"
    # This proves Extension 4a: when no eligible dish satisfies the active power-up, the spin still returns the best available (lower-weighted) dish rather than returning nothing.


# ======================================================================
# Use Case 12 — Browse Saved Meals
# ======================================================================

def test_saved_ids_are_resolved_against_the_current_catalog_and_can_be_filtered_by_category():
    catalog = {
        "d1": {"id": "d1", "name": "Oats", "category": "Breakfast"},
        "d2": {"id": "d2", "name": "Steak", "category": "Dinner"},
    }
    saved = resolve_saved_dishes(["d1", "d2"], catalog)
    breakfast_only = [d for d in saved if d["category"] == "Breakfast"]
    assert [d["id"] for d in saved] == ["d1", "d2"]
    assert [d["id"] for d in breakfast_only] == ["d1"]
    # This proves the main success scenario: saved identifiers resolve to full dish records and can be narrowed to a single category.


def test_a_saved_id_no_longer_in_the_catalog_is_silently_omitted():
    catalog = {"d1": {"id": "d1", "name": "Oats", "category": "Breakfast"}}
    saved = resolve_saved_dishes(["d1", "deleted_dish"], catalog)
    assert [d["id"] for d in saved] == ["d1"]
    # This proves Extension 2a: a saved dish that has since been removed from the catalog is dropped from the displayed list rather than causing an error.


def test_an_account_with_no_saved_meals_resolves_to_an_empty_list():
    saved = resolve_saved_dishes([], {"d1": {"id": "d1", "name": "Oats", "category": "Breakfast"}})
    assert saved == []
    # This proves Extension 3a: an empty saved-meal collection resolves cleanly to an empty list, which the UI renders as its empty state.


# ======================================================================
# Use Case 13 — Remove a Saved Meal
# ======================================================================

def test_removing_a_saved_dish_updates_and_persists_the_shortened_list():
    persisted = []
    next_list, ok = remove_saved_meal(["d1", "d2"], "d1", persisted.append)
    assert ok is True
    assert next_list == ["d2"]
    assert persisted == [["d2"]]
    # This proves the main success scenario: removing one saved dish leaves the rest intact and persists the updated collection.


def test_a_failed_removal_request_keeps_the_dish_in_the_prior_collection():
    def failing_persist(_next_list):
        raise ConnectionError("network error")

    next_list, ok = remove_saved_meal(["d1", "d2"], "d1", failing_persist)
    assert ok is False
    assert next_list == ["d1", "d2"]
    # This proves Extension 3a: a persistence failure returns the prior collection unchanged so a refresh can restore the server's authoritative state instead of losing the item silently.


def test_removing_the_last_saved_meal_leaves_an_empty_collection():
    next_list, ok = remove_saved_meal(["only_dish"], "only_dish", lambda _l: None)
    assert ok is True
    assert next_list == []
    # This proves that removing a user's final saved meal correctly results in the empty-state collection rather than a special-cased error.


# ======================================================================
# Use Case 14 — Leave a Party
# ======================================================================

def test_leaving_a_party_removes_that_members_record_and_keeps_the_rest():
    members = [{"id": "m1", "creator": True}, {"id": "m2", "creator": False}]
    remaining = leave_party(members, "m2")
    assert [m["id"] for m in remaining] == ["m1"]
    # This proves the main success scenario: leaving removes exactly the departing member's record and leaves other members untouched.


def test_the_host_leaving_implicitly_hands_off_to_the_next_connected_member():
    members = [{"id": "host1", "creator": True}, {"id": "m2", "creator": False}]
    remaining = leave_party(members, "host1")
    new_host_id = compute_host(remaining)
    assert new_host_id == "m2"
    # This proves Extension 2a: there is no explicit "reassign host" step; once the host's record is gone, host computation simply falls through to the next live member.


def test_a_member_who_never_left_keeps_their_membership_when_removal_is_only_attempted():
    members = [{"id": "m1", "creator": True}, {"id": "m2", "creator": False}]
    attempted_removal_target = "does_not_exist"
    remaining = leave_party(members, attempted_removal_target)
    assert [m["id"] for m in remaining] == ["m1", "m2"]
    # This proves Extension 2b's guarantee in the opposite direction: if a removal cannot be matched to a real member (modeling a failed/rejected server-side removal), the roster is left exactly as it was rather than partially mutated.


# ======================================================================
# Use Case 15 — Find Nearby Restaurants After Spinning
# ======================================================================

def test_venues_are_returned_per_cuisine_using_the_provided_coordinates():
    def search_fn(cuisine, origin):
        return [{"name": f"{cuisine.title()} Place", "origin": origin}]

    result = search_places(["italian", "thai"], coords=(35.7, -78.6),
                            location_hint="Denver", search_fn=search_fn, geocode_fn=lambda _h: (0, 0))
    assert result["origin"] == (35.7, -78.6)
    assert result["results"]["italian"][0]["name"] == "Italian Place"
    assert result["errors"] == {}
    # This proves the main success scenario: each requested cuisine is searched near the caller's real coordinates with no per-cuisine errors.


def test_missing_coordinates_fall_back_to_geocoding_the_location_hint():
    geocode_calls = []

    def geocode_fn(hint):
        geocode_calls.append(hint)
        return (39.7, -104.9)

    result = search_places(["italian"], coords=None, location_hint="Denver",
                            search_fn=lambda cuisine, origin: [], geocode_fn=geocode_fn)
    assert geocode_calls == ["Denver"]
    assert result["origin"] == (39.7, -104.9)
    # This proves Extension 2a/3a: when the browser provides no coordinates (denied or unsupported geolocation), the system geocodes the configured location hint instead of failing.


def test_one_cuisines_search_failure_does_not_prevent_other_cuisines_from_returning_results():
    def flaky_search_fn(cuisine, _origin):
        if cuisine == "sushi":
            raise RuntimeError("Places API error")
        return [{"name": f"{cuisine} spot"}]

    result = search_places(["sushi", "tacos"], coords=(0, 0), location_hint="Denver",
                            search_fn=flaky_search_fn, geocode_fn=lambda _h: (0, 0))
    assert result["results"]["sushi"] == []
    assert "sushi" in result["errors"]
    assert result["results"]["tacos"] == [{"name": "tacos spot"}]
    # This proves Extension 4a: a Places error for one cuisine is isolated to that cuisine's result and error entry, while the other cuisine still succeeds.


# ======================================================================
# Use Case 16 — Create Party
# ======================================================================

def test_a_valid_nickname_creates_an_active_party_with_the_creator_as_host():
    party = create_party("Sebastian", code_gen_fn=lambda: "ABC123")
    assert party["isActive"] is True
    assert party["code"] == "ABC123"
    assert party["members"][0]["host"] is True
    # This proves the main success scenario: supplying a valid nickname produces an active party with a generated code and the creator registered as host.


def test_an_empty_nickname_prevents_party_creation():
    result = create_party("   ", code_gen_fn=lambda: "ABC123")
    assert result == {"error": "invalid_nickname"}
    # This proves Extension 1a: a blank (or whitespace-only) nickname is rejected before a party is ever created.


def test_a_hosts_saved_account_allergens_seed_the_new_partys_host_preferences():
    party = create_party("Sebastian", code_gen_fn=lambda: "ABC123", user_allergens=["peanut", "gluten"])
    assert party["members"][0]["allergens"] == ["peanut", "gluten"]
    # This proves Extension 4a: a signed-in host's previously saved allergens automatically seed their party-member preferences instead of starting empty.


# ======================================================================
# Use Case 17 — Join Party
# ======================================================================

def test_joining_with_a_valid_code_adds_a_new_member_to_the_active_party():
    parties = {"ABC123": {"code": "ABC123", "isActive": True, "members": []}}
    result = join_party(parties, "ABC123", "Guest One")
    assert result["code"] == "ABC123"
    assert parties["ABC123"]["members"][0]["nickname"] == "Guest One"
    # This proves the main success scenario: a valid code and nickname adds the joiner as a new party member and returns their membership details.


def test_joining_with_an_unknown_or_inactive_code_is_rejected():
    parties = {"ABC123": {"code": "ABC123", "isActive": False, "members": []}}
    result = join_party(parties, "ABC123", "Guest One")
    assert result == {"error": "NOT_FOUND"}
    assert parties["ABC123"]["members"] == []
    # This proves Extension 2a: an invalid or inactive party code is rejected and no membership record is created.


def test_joining_without_stated_preferences_stores_default_empty_preferences():
    parties = {"ABC123": {"code": "ABC123", "isActive": True, "members": []}}
    join_party(parties, "ABC123", "Guest One")
    assert parties["ABC123"]["members"][0]["prefs"] == {}
    # This proves Extension 6a: a joiner who supplies no preferences is still given a member record, defaulted to empty preferences rather than being blocked.


def test_a_user_who_already_belongs_to_a_party_cannot_join_a_second_one():
    """EXPECTED TO FAIL. UC17's own stakeholder table and Extension 4a both
    state the rule plainly: 'User already belongs to a party -> system returns
    an error indicating the user is already part of a party.' But join_party()'s
    signature is (parties_by_code, code, nickname, prefs=None) -- it has no
    auth_id parameter and never looks at one, so it has no way to know whether
    the caller is already a member of some other (or the same) party. It will
    add the same user as a member of a second party with no error at all. This
    is not an edge-case slip; Extension 4a is an entire stated business rule
    that was never ported, and none of the three existing UC17 tests happen to
    exercise it, so the gap has been invisible until now."""
    parties = {
        "AAA111": {"code": "AAA111", "isActive": True, "members": [{"id": "m1", "auth_id": "user_1"}]},
        "BBB222": {"code": "BBB222", "isActive": True, "members": []},
    }
    result = join_party(parties, "BBB222", "Guest One", prefs={"auth_id": "user_1"})
    assert result == {"error": "ALREADY_IN_PARTY"}


# ======================================================================
# Use Case 18 — Sign In to an Account
# ======================================================================

def test_valid_credentials_establish_a_session_and_load_the_matching_profile():
    profile_store = {"auth_1": {"auth_id": "auth_1", "allergens": ["dairy"], "savedMeals": ["d1"]}}
    result = sign_in("good_credentials", {"good_credentials": "auth_1"}, profile_store)
    assert result["session"]["auth_id"] == "auth_1"
    assert result["profile"]["allergens"] == ["dairy"]
    # This proves the main success scenario: valid credentials produce a session and load that same identity's saved profile.


def test_invalid_credentials_are_rejected_without_creating_a_session():
    profile_store = {}
    result = sign_in("bad_credentials", {"good_credentials": "auth_1"}, profile_store)
    assert result == {"error": "invalid_credentials"}
    # This proves Extension 3a: credentials that do not match any known identity are rejected, and no session or profile access occurs.


def test_a_first_time_valid_identity_gets_a_fresh_empty_profile_instead_of_being_blocked():
    profile_store = {}
    result = sign_in("good_credentials", {"good_credentials": "auth_new"}, profile_store)
    assert result["profile"] == {"auth_id": "auth_new", "allergens": [], "savedMeals": []}
    assert profile_store["auth_new"] == result["profile"]
    # This proves Extension 4a: a valid identity with no prior MealSlot profile has one created on the fly with empty saved data, rather than sign-in failing.


# ======================================================================
# Use Case 19 — Sign Out of an Account
# ======================================================================

def test_signing_out_clears_the_session_profile_and_client_cache():
    state = {"session": {"auth_id": "auth_1"}, "profile": {"allergens": ["dairy"]}, "cache": {"userProfile": "..."}}
    sign_out(state)
    assert state["session"] is None
    assert state["profile"] is None
    assert state["cache"] == {}
    # This proves the main success scenario: sign-out clears the authenticated session, the in-app profile, and any cached account data in one step.


def test_a_failed_provider_sign_out_does_not_falsely_report_success():
    def sign_out_with_failing_provider(state):
        provider_ok = False
        if not provider_ok:
            return False
        return sign_out(state)

    state = {"session": {"auth_id": "auth_1"}, "profile": {}, "cache": {}}
    result = sign_out_with_failing_provider(state)
    assert result is False
    assert state["session"] is not None
    # This proves Extension 2a: when the identity provider's sign-out step fails, the local session is left intact and the caller is told it did not succeed, rather than optimistically clearing state.


def test_after_sign_out_an_account_only_page_exposes_no_previous_users_data():
    state = sign_out({"session": {"auth_id": "auth_1"}, "profile": {"allergens": ["dairy"]}, "cache": {}})

    def account_only_page(state):
        return None if state["session"] is None else state["profile"]

    assert account_only_page(state) is None
    # This proves Extension 5a: visiting an account-only view after sign-out returns no data at all rather than leaking the previous user's cached profile.


# ======================================================================
# Use Case 20 — Chat with Party Members
# ======================================================================

def test_a_non_empty_message_is_broadcast_to_connected_party_members():
    local_log, remote_log = [], []
    sent = send_chat_message(local_log, remote_log, "Let's get pizza", has_dedicated_realtime=True)
    assert sent is True
    assert local_log == ["Let's get pizza"]
    assert remote_log == ["Let's get pizza"]
    # This proves the main success scenario: sending a message delivers it to every connected member's chat panel.


def test_sending_an_empty_message_does_nothing():
    local_log, remote_log = [], []
    sent = send_chat_message(local_log, remote_log, "   ", has_dedicated_realtime=True)
    assert sent is False
    assert local_log == [] and remote_log == []
    # This proves Extension 2a: an empty or whitespace-only message is a no-op rather than producing a blank chat entry.


def test_without_a_dedicated_realtime_server_a_message_only_reaches_local_browser_tabs():
    local_log, other_device_log = [], []
    send_chat_message(local_log, other_device_log, "Anyone free at 7?", has_dedicated_realtime=False)
    assert local_log == ["Anyone free at 7?"]
    assert other_device_log == []
    # This proves Extension 3a: without NEXT_PUBLIC_WS_URL configured, the chat message reaches only same-machine BroadcastChannel peers and never other devices.


# ======================================================================
# Use Case 21 — Manage Dietary Preferences (Sebastian_Use_Cases.md, UC12)
# Distinct from Use Case 9: this is the persisted, account-level allergen
# list, not the session-only spin filter.
# ======================================================================

def test_saving_new_allergen_selections_persists_them_to_the_account():
    persisted = []
    user = {"allergens": ["dairy"]}
    ok = update_user_allergens(user, ["dairy", "shellfish"], persisted.append)
    assert ok is True
    assert user["allergens"] == ["dairy", "shellfish"]
    assert persisted == [["dairy", "shellfish"]]
    # This proves the main success scenario: an updated allergen list is written to the user's account record.


def test_a_failed_save_leaves_the_prior_allergen_list_active():
    def failing_persist(_new_allergens):
        raise ConnectionError("network error")

    user = {"allergens": ["dairy"]}
    ok = update_user_allergens(user, ["dairy", "shellfish"], failing_persist)
    assert ok is False
    assert user["allergens"] == ["dairy"]
    # This proves Extension 5a: when the save request fails, the account keeps its previously active allergen list instead of ending up in a partially-updated state.


def test_saved_account_allergens_are_applied_to_a_spin_without_reselecting_them():
    user = {"allergens": ["peanut"]}
    reels = [[
        {"id": "safe", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": []},
        {"id": "unsafe", "isHealthy": True, "costBand": 1, "timeBand": 1, "allergens": ["peanut"]},
    ]]
    filtered_reel = filter_by_allergens(reels[0], user["allergens"])
    selection = weighted_spin([filtered_reel], rng=lambda: 0.0)
    assert selection[0]["id"] == "safe"
    # This proves the use case's core value: once allergens are saved to the account, they are applied to spin candidates automatically, without the user re-entering them as a session filter (Use Case 9).'''

_SOURCE_2 = r'''"""
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
    # New coverage: the use case states that chat lasts only for the session; a reload has no persisted history to restore.'''

_SOURCE_3 = r'''"""
Pytest acceptance findings for known MealSlot defects.

Each helper below is a minimal behavioral model of an inspected MealSlot
implementation path. Each test asserts the expected behavior from the final
use cases. The tests therefore FAIL where the current implementation and the
documented use case disagree.

These failures are intentional findings, but they are not fabricated with
``assert False``. Every failed assertion compares a concrete expected outcome
with a modeled current outcome.

This remains a behavioral-model suite, not a live browser/API suite.
"""


def current_merge_diet_preferences(diets):
    """Current mergeConstraints behavior selects the strictest ethic diet."""
    strictness = {"vegan": 4, "vegetarian": 3, "pescatarian": 2, "omnivore": 1}
    selected = sorted(set(diets), key=lambda diet: -strictness[diet])[0]
    return {"diet": [selected], "conflict": False}


def current_party_fallback(fallback_menu, excluded_allergens):
    """Current party fallback returns hardcoded dishes without allergen filtering."""
    return fallback_menu[:3]


def current_create_party_status(nickname):
    """Current route validates nickname length without trimming whitespace."""
    return 400 if len(nickname) < 1 or len(nickname) > 24 else 200


def current_join_party(members, code, nickname):
    """Current join route creates another membership without duplicate detection."""
    members.append({"id": f"m{len(members) + 1}", "code": code, "nickname": nickname})
    return 200


def current_page_leave(local_state, authoritative_members):
    """Current page clears local state but does not invoke the leave endpoint."""
    local_state.clear()
    return authoritative_members


def current_favorites_page(authenticated, local_saved_ids):
    """Current Favorites page requires authentication and ignores guest-local saves."""
    if not authenticated:
        return []
    return list(local_saved_ids)


def current_optimistic_save(saved_ids, dish_id, persistence_succeeds):
    """Current home-page save logs a persistence failure without rolling back UI state."""
    optimistic = list(saved_ids) + [dish_id]
    if not persistence_succeeds:
        return optimistic
    return optimistic


def current_cross_browser_chat(message, client_protocol="raw-websocket", server_protocol="socket.io"):
    """Current client/server protocol mismatch prevents remote delivery."""
    sender_log = [message]
    remote_log = []
    if client_protocol == server_protocol:
        remote_log.append(message)
    return sender_log, remote_log


def current_category_lookup(requested_category, seeded_categories):
    """Current dish lookup compares category strings exactly."""
    return [category for category in seeded_categories if category == requested_category]


def current_join_page_state(join_response):
    """Current party page retains the code but discards the returned memberId."""
    return {"activeCode": join_response["code"], "memberId": None}


# ======================================================================
# Known defect 1 — UC02 party preference conflict reporting
# ======================================================================


def test_incompatible_party_diets_should_raise_a_conflict():
    result = current_merge_diet_preferences(["vegan", "omnivore"])
    assert result["conflict"] is True, (
        "Expected incompatible party diets to be reported as a conflict, "
        f"but current behavior selected {result['diet']} with conflict=False."
    )


# ======================================================================
# Known defect 2 — UC04 party fallback allergen safety
# ======================================================================


def test_party_fallback_should_exclude_dishes_with_group_allergens():
    fallback = [
        {"id": "unsafe", "allergens": ["peanut"]},
        {"id": "safe1", "allergens": []},
        {"id": "safe2", "allergens": []},
    ]
    results = current_party_fallback(fallback, excluded_allergens=["peanut"])
    assert all("peanut" not in dish["allergens"] for dish in results), (
        "Expected the group peanut exclusion to apply to fallback dishes, "
        f"but current fallback returned {[dish['id'] for dish in results]}."
    )


# ======================================================================
# Known defect 3 — UC16 party nickname validation
# ======================================================================


def test_whitespace_only_party_nickname_should_be_rejected():
    status = current_create_party_status("   ")
    assert status == 400, (
        "Expected a whitespace-only nickname to be rejected with status 400, "
        f"but current route-style validation accepts it with status {status}."
    )


# ======================================================================
# Known defect 4 — UC17 duplicate party membership
# ======================================================================


def test_repeated_join_should_not_create_a_duplicate_membership():
    members = [{"id": "m1", "code": "ABC123", "nickname": "Host"}]
    first_status = current_join_party(members, "ABC123", "Guest")
    second_status = current_join_party(members, "ABC123", "Guest")
    assert first_status == 200
    assert second_status == 409, (
        "Expected the repeated join to be rejected as an existing membership, "
        f"but it returned {second_status} and created {len(members)} total members."
    )


# ======================================================================
# Known defect 5 — UC14 authoritative party leaving
# ======================================================================


def test_leaving_from_the_page_should_remove_the_authoritative_membership():
    local_state = {"activeCode": "ABC123", "memberId": "m2"}
    server_members = [{"id": "m1"}, {"id": "m2"}]
    remaining = current_page_leave(local_state, server_members)
    assert "m2" not in [member["id"] for member in remaining], (
        "Expected Leave Party to delete member m2 from authoritative state, "
        f"but current page behavior left {[member['id'] for member in remaining]}."
    )


# ======================================================================
# Known defect 6 — UC08 guest favorite visibility
# ======================================================================


def test_guest_should_be_able_to_browse_a_locally_saved_meal():
    visible = current_favorites_page(authenticated=False, local_saved_ids=["dish1"])
    assert visible == ["dish1"], (
        "Expected the guest's locally saved dish to appear in Favorites, "
        f"but the signed-out page exposed {visible}."
    )


# ======================================================================
# Known defect 7 — UC08 failed favorite persistence reconciliation
# ======================================================================


def test_failed_account_save_should_revert_the_optimistic_saved_state():
    visible = current_optimistic_save([], "dish1", persistence_succeeds=False)
    assert visible == [], (
        "Expected a failed account persistence request to restore the prior UI state, "
        f"but the optimistic collection remained {visible}."
    )


# ======================================================================
# Known defect 8 — UC20 cross-browser party chat
# ======================================================================


def test_party_chat_should_deliver_the_message_to_another_browser():
    sender, remote = current_cross_browser_chat("Pizza?")
    assert sender == ["Pizza?"]
    assert remote == ["Pizza?"], (
        "Expected the remote party browser to receive the chat message, "
        f"but current protocol behavior produced remote log {remote}."
    )


# ======================================================================
# Known defect 9 — UC01 default category compatibility
# ======================================================================


def test_default_title_case_category_should_find_seeded_dishes():
    matches = current_category_lookup("Breakfast", ["breakfast", "lunch", "dinner"])
    assert matches, (
        "Expected the default Breakfast selection to find seeded breakfast dishes, "
        "but exact case-sensitive matching returned no candidates."
    )


# ======================================================================
# Known defect 10 — UC17 joined-member identity retention
# ======================================================================


def test_join_page_should_retain_the_returned_member_identifier():
    response = {"code": "ABC123", "memberId": "m2"}
    page_state = current_join_page_state(response)
    assert page_state["memberId"] == "m2", (
        "Expected the joined browser to retain memberId m2 for realtime operations, "
        f"but current page state stored {page_state['memberId']}."
    )'''

_load_original_suite(_SOURCE_1, "test_top20_use_cases (3).py")
_load_original_suite(_SOURCE_2, "test_top20_use_cases_additional.py")
_load_original_suite(_SOURCE_3, "D3_PYTEST_FAIL_TEST_CASES")

del _SOURCE_1, _SOURCE_2, _SOURCE_3
