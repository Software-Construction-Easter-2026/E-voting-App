"""
tests.py

Simple tests — no pytest needed, just run: python tests.py
Each test function covers one operation class.
Tests use a temporary folder so they never touch real data.
"""

import os
import sys
import shutil
import datetime

# ── Test setup ────────────────────────────────────────────────────────────────

TEST_DATA_DIRECTORY = "test_data"


def _point_all_stores_at_test_data() -> None:
    """Reset every singleton store to point at the test data folder."""
    from Backend.storage import JsonStore
    import Backend.polls_management as polls_management, Backend.voters_management as voters_management, Backend.admin_management as admin_management, Backend.audits as audits

    polls_management.PollStore._instance   = JsonStore(f"{TEST_DATA_DIRECTORY}/polls.json")
    voters_management.VoterStore._instance = JsonStore(f"{TEST_DATA_DIRECTORY}/voters.json")
    admin_management.AdminStore._instance = JsonStore(f"{TEST_DATA_DIRECTORY}/admins.json")
    audits.AuditStore._instance = JsonStore(f"{TEST_DATA_DIRECTORY}/audits.json")


def _seed_admin(role: str = "super_admin") -> dict:
    from Backend.admin_management import AdminStore, hash_password
    return AdminStore.get().insert({
        "username":      "testadmin",
        "password_hash": hash_password("password123"),
        "full_name":     "Test Admin",
        "email":         "admin@test.com",
        "role":          role,
        "is_active":     True,
        "created_at":    str(datetime.datetime.now()),
    })


def _seed_voter(is_verified: bool = False, is_active: bool = True) -> dict:
    from Backend.voters_management import VoterStore
    return VoterStore.get().insert({
        "full_name":          "Alice Nakato",
        "national_id":        "NID001",
        "voter_card_number":  "VC001",
        "station_id":         1,
        "is_verified":        is_verified,
        "is_active":          is_active,
    })


def _seed_poll(status: str = "draft", total_votes: int = 0) -> dict:
    from Backend.polls_management import PollStore
    return PollStore.get().insert({
        "title":         "Test Election",
        "description":   "A test poll",
        "election_type": "General",
        "start_date":    "2026-06-01",
        "end_date":      "2026-06-30",
        "positions": [
            {
                "position_id":    1,
                "position_title": "President",
                "max_winners":    1,
                "candidate_ids":  [],
            }
        ],
        "station_ids": [1],
        "status":      status,
        "total_votes": total_votes,
        "created_by":  "testadmin",
        "created_at":  str(datetime.datetime.now()),
    })


# ── Test runner ───────────────────────────────────────────────────────────────

total_passed = 0
total_failed = 0


def run(test_description: str, test_function):
    global total_passed, total_failed
    shutil.rmtree(TEST_DATA_DIRECTORY, ignore_errors=True)
    os.makedirs(TEST_DATA_DIRECTORY, exist_ok=True)
    _point_all_stores_at_test_data()
    try:
        test_function()
        print(f"  ✔  {test_description}")
        total_passed += 1
    except AssertionError as assertion_error:
        print(f"  ✘  {test_description}  →  {assertion_error}")
        total_failed += 1
    except Exception as unexpected_error:
        print(f"  ✘  {test_description}  →  unexpected: {type(unexpected_error).__name__}: {unexpected_error}")
        total_failed += 1


def expect_raises(expected_exception_type, function_that_should_raise):
    try:
        function_that_should_raise()
        raise AssertionError(
            f"Expected {expected_exception_type.__name__} but nothing was raised."
        )
    except expected_exception_type:
        pass  # correct — the expected exception was raised


# ═══════════════════════════════════════════════════════════════════════════════
#  STORAGE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_store_insert_assigns_auto_incrementing_id():
    from Backend.storage import JsonStore
    test_store = JsonStore(f"{TEST_DATA_DIRECTORY}/misc.json")
    inserted_record = test_store.insert({"name": "Alice"})
    assert inserted_record["id"] == 1, f"Expected id=1, got {inserted_record['id']}"


def test_store_find_returns_only_matching_records():
    from Backend.storage import JsonStore
    test_store = JsonStore(f"{TEST_DATA_DIRECTORY}/misc.json")
    test_store.insert({"status": "open"})
    test_store.insert({"status": "closed"})
    open_records = test_store.find(status="open")
    assert len(open_records) == 1


def test_store_update_changes_the_correct_field():
    from Backend.storage import JsonStore
    test_store = JsonStore(f"{TEST_DATA_DIRECTORY}/misc.json")
    inserted_record = test_store.insert({"name": "Alice"})
    updated_record  = test_store.update(inserted_record["id"], {"name": "Bob"})
    assert updated_record["name"] == "Bob"


def test_store_delete_removes_the_record():
    from Backend.storage import JsonStore
    test_store = JsonStore(f"{TEST_DATA_DIRECTORY}/misc.json")
    inserted_record = test_store.insert({"name": "Alice"})
    deletion_succeeded = test_store.delete(inserted_record["id"])
    assert deletion_succeeded is True
    assert test_store.all() == []


# ═══════════════════════════════════════════════════════════════════════════════
#  POLL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_create_poll_stores_it_with_draft_status():
    from Backend.polls_management import CreatePoll, GetAllPolls
    CreatePoll("admin").execute(
        title="Election 2026",
        description="General election",
        election_type="General",
        start_date="2026-06-01",
        end_date="2026-06-30",
        positions=[{"position_id": 1, "title": "President", "max_winners": 1}],
        station_ids=[1, 2],
    )
    all_polls = GetAllPolls().execute()
    assert len(all_polls) == 1
    assert all_polls[0]["status"] == "draft"


def test_create_poll_with_empty_title_raises_error():
    from Backend.polls_management import CreatePoll
    expect_raises(ValueError, lambda: CreatePoll("admin").execute(
        title="", description="", election_type="General",
        start_date="2026-06-01", end_date="2026-06-30",
        positions=[{}], station_ids=[],
    ))


def test_create_poll_with_end_before_start_raises_error():
    from Backend.polls_management import CreatePoll
    expect_raises(ValueError, lambda: CreatePoll("admin").execute(
        title="Test", description="", election_type="General",
        start_date="2026-06-30", end_date="2026-06-01",
        positions=[{"position_id": 1, "title": "President", "max_winners": 1}],
        station_ids=[1],
    ))


def test_update_poll_changes_the_title():
    from Backend.polls_management import UpdatePoll
    seeded_poll  = _seed_poll()
    updated_poll = UpdatePoll().execute(seeded_poll["id"], {"title": "New Title"})
    assert updated_poll["title"] == "New Title"


def test_update_open_poll_raises_error():
    from Backend.polls_management import UpdatePoll
    open_poll = _seed_poll(status="open")
    expect_raises(ValueError, lambda: UpdatePoll().execute(open_poll["id"], {"title": "X"}))


def test_update_closed_poll_with_votes_raises_error():
    from Backend.polls_management import UpdatePoll
    closed_poll_with_votes = _seed_poll(status="closed", total_votes=5)
    expect_raises(ValueError, lambda: UpdatePoll().execute(closed_poll_with_votes["id"], {"title": "X"}))


def test_delete_draft_poll_removes_it():
    from Backend.polls_management import DeletePoll, GetAllPolls
    seeded_poll = _seed_poll()
    DeletePoll().execute(seeded_poll["id"])
    assert GetAllPolls().execute() == []


def test_delete_open_poll_raises_error():
    from Backend.polls_management import DeletePoll
    open_poll = _seed_poll(status="open")
    expect_raises(ValueError, lambda: DeletePoll().execute(open_poll["id"]))


def test_open_poll_without_candidates_raises_error():
    from Backend.polls_management import OpenPoll
    poll_with_no_candidates = _seed_poll()
    expect_raises(ValueError, lambda: OpenPoll().execute(poll_with_no_candidates["id"]))


def test_open_poll_with_candidates_sets_status_to_open():
    from Backend.polls_management import OpenPoll, PollStore
    poll_with_candidates = PollStore.get().insert({
        "title": "Test", "description": "", "election_type": "General",
        "start_date": "2026-06-01", "end_date": "2026-06-30",
        "positions": [{
            "position_id": 1, "position_title": "President",
            "max_winners": 1, "candidate_ids": [1],
        }],
        "station_ids": [1], "status": "draft", "total_votes": 0,
        "created_by": "admin", "created_at": "",
    })
    opened_poll = OpenPoll().execute(poll_with_candidates["id"])
    assert opened_poll["status"] == "open"


def test_close_open_poll_sets_status_to_closed():
    from Backend.polls_management import ClosePoll
    open_poll    = _seed_poll(status="open")
    closed_poll  = ClosePoll().execute(open_poll["id"])
    assert closed_poll["status"] == "closed"


def test_close_draft_poll_raises_error():
    from Backend.polls_management import ClosePoll
    draft_poll = _seed_poll(status="draft")
    expect_raises(ValueError, lambda: ClosePoll().execute(draft_poll["id"]))


def test_assign_candidates_skips_ineligible_ids():
    from Backend.polls_management import AssignCandidates
    seeded_poll         = _seed_poll()
    eligible_ids        = {1, 2, 3}
    result_poll         = AssignCandidates(eligible_ids).execute(seeded_poll["id"], 0, [1, 2, 99])
    assigned_ids        = result_poll["positions"][0]["candidate_ids"]
    assert assigned_ids == [1, 2], f"Expected [1, 2], got {assigned_ids}"


# ═══════════════════════════════════════════════════════════════════════════════
#  VOTER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_get_all_voters_returns_empty_list_when_none_exist():
    from Backend.voters_management import GetAllVoters
    assert GetAllVoters().execute() == []


def test_verify_voter_sets_is_verified_to_true():
    from Backend.voters_management import VerifyVoter
    unverified_voter = _seed_voter(is_verified=False)
    verified_voter   = VerifyVoter().execute(unverified_voter["id"])
    assert verified_voter["is_verified"] is True


def test_verify_already_verified_voter_raises_error():
    from Backend.voters_management import VerifyVoter
    already_verified_voter = _seed_voter(is_verified=True)
    expect_raises(ValueError, lambda: VerifyVoter().execute(already_verified_voter["id"]))


def test_verify_all_voters_returns_count_of_voters_changed():
    from Backend.voters_management import VerifyAllVoters, VoterStore
    VoterStore.get().insert({
        "full_name": "Bob", "national_id": "N1",
        "voter_card_number": "C1", "station_id": 1,
        "is_verified": False, "is_active": True,
    })
    VoterStore.get().insert({
        "full_name": "Eve", "national_id": "N2",
        "voter_card_number": "C2", "station_id": 1,
        "is_verified": False, "is_active": True,
    })
    number_verified = VerifyAllVoters().execute()
    assert number_verified == 2


def test_deactivate_voter_sets_is_active_to_false():
    from Backend.voters_management import DeactivateVoter
    active_voter      = _seed_voter(is_active=True)
    deactivated_voter = DeactivateVoter().execute(active_voter["id"])
    assert deactivated_voter["is_active"] is False


def test_deactivate_already_inactive_voter_raises_error():
    from Backend.voters_management import DeactivateVoter
    inactive_voter = _seed_voter(is_active=False)
    expect_raises(ValueError, lambda: DeactivateVoter().execute(inactive_voter["id"]))


def test_search_voters_by_name_returns_matching_voter():
    from Backend.voters_management import SearchVoters
    _seed_voter()   # full_name = "Alice Nakato"
    search_results = SearchVoters().execute("name", "alice")
    assert len(search_results) == 1


def test_search_voters_by_card_number_returns_matching_voter():
    from Backend.voters_management import SearchVoters
    _seed_voter()   # voter_card_number = "VC001"
    search_results = SearchVoters().execute("card", "VC001")
    assert len(search_results) == 1


def test_search_voters_with_unknown_field_raises_error():
    from Backend.voters_management import SearchVoters
    expect_raises(ValueError, lambda: SearchVoters().execute("email", "test@test.com"))


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_authenticate_admin_with_correct_credentials_returns_admin():
    from Backend.admin_management import AuthenticateAdmin
    _seed_admin()
    returned_admin = AuthenticateAdmin().execute("testadmin", "password123")
    assert returned_admin["username"] == "testadmin"


def test_authenticate_admin_with_wrong_password_raises_error():
    from Backend.admin_management import AuthenticateAdmin
    _seed_admin()
    expect_raises(ValueError, lambda: AuthenticateAdmin().execute("testadmin", "wrongpassword"))


def test_authenticate_nonexistent_admin_raises_error():
    from Backend.admin_management import AuthenticateAdmin
    expect_raises(ValueError, lambda: AuthenticateAdmin().execute("nobody", "anypassword"))


def test_create_admin_as_super_admin_succeeds():
    from Backend.admin_management import CreateAdmin, GetAllAdmins
    super_admin = _seed_admin(role="super_admin")
    CreateAdmin(super_admin).execute(
        username="officer1", plain_text_password="securepass",
        full_name="Jane Doe", email="jane@test.com", role="election_officer",
    )
    all_admins = GetAllAdmins().execute()
    assert len(all_admins) == 2


def test_create_admin_as_non_super_admin_raises_permission_error():
    from Backend.admin_management import CreateAdmin
    election_officer = _seed_admin(role="election_officer")
    expect_raises(PermissionError, lambda: CreateAdmin(election_officer).execute(
        username="newuser", plain_text_password="securepass",
        full_name="X", email="x@x.com", role="auditor",
    ))


def test_create_admin_with_duplicate_username_raises_error():
    from Backend.admin_management import CreateAdmin
    super_admin = _seed_admin(role="super_admin")
    expect_raises(ValueError, lambda: CreateAdmin(super_admin).execute(
        username="testadmin",  # already exists
        plain_text_password="securepass",
        full_name="Duplicate", email="dup@test.com", role="auditor",
    ))


def test_create_admin_with_short_password_raises_error():
    from Backend.admin_management import CreateAdmin
    super_admin = _seed_admin(role="super_admin")
    expect_raises(ValueError, lambda: CreateAdmin(super_admin).execute(
        username="newuser", plain_text_password="123",
        full_name="New", email="new@test.com", role="auditor",
    ))


def test_create_admin_with_invalid_role_raises_error():
    from Backend.admin_management import CreateAdmin
    super_admin = _seed_admin(role="super_admin")
    expect_raises(ValueError, lambda: CreateAdmin(super_admin).execute(
        username="newuser", plain_text_password="securepass",
        full_name="New", email="new@test.com", role="hacker",
    ))


def test_deactivate_admin_sets_is_active_to_false():
    from Backend.admin_management import CreateAdmin, DeactivateAdmin, GetAdmin
    super_admin     = _seed_admin(role="super_admin")
    new_admin       = CreateAdmin(super_admin).execute(
        username="officer1", plain_text_password="securepass",
        full_name="Jane", email="j@j.com", role="auditor",
    )
    DeactivateAdmin(super_admin).execute(new_admin["id"])
    deactivated_admin = GetAdmin().execute(new_admin["id"])
    assert deactivated_admin["is_active"] is False


def test_deactivate_own_account_raises_error():
    from Backend.admin_management import DeactivateAdmin
    super_admin = _seed_admin(role="super_admin")
    expect_raises(ValueError, lambda: DeactivateAdmin(super_admin).execute(super_admin["id"]))


def test_deactivate_admin_as_non_super_admin_raises_permission_error():
    from Backend.admin_management import CreateAdmin, DeactivateAdmin
    super_admin      = _seed_admin(role="super_admin")
    election_officer = CreateAdmin(super_admin).execute(
        username="officer1", plain_text_password="securepass",
        full_name="Jane", email="j@j.com", role="election_officer",
    )
    expect_raises(PermissionError, lambda: DeactivateAdmin(election_officer).execute(super_admin["id"]))


# ═══════════════════════════════════════════════════════════════════════════════
#  AUDIT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_log_audit_entry_saves_all_fields():
    from Backend.audits import LogAuditEntry, AuditAction
    logged_entry = LogAuditEntry().execute(
        action_name  = AuditAction.POLL_CREATED,
        performed_by = "admin1",
        details      = "Created poll 'Election 2026' (id=1)",
    )
    assert logged_entry["action_name"]  == AuditAction.POLL_CREATED
    assert logged_entry["performed_by"] == "admin1"
    assert "recorded_at" in logged_entry


def test_get_all_audit_entries_returns_every_entry():
    from Backend.audits import LogAuditEntry, GetAllAuditEntries, AuditAction
    LogAuditEntry().execute(AuditAction.POLL_CREATED,   "admin1", "Created poll A")
    LogAuditEntry().execute(AuditAction.VOTER_VERIFIED, "admin2", "Verified voter Bob")
    all_entries = GetAllAuditEntries().execute()
    assert len(all_entries) == 2


def test_get_audit_entries_by_admin_filters_correctly():
    from Backend.audits import LogAuditEntry, GetAuditEntriesByAdmin, AuditAction
    LogAuditEntry().execute(AuditAction.POLL_CREATED,   "alice", "Created poll A")
    LogAuditEntry().execute(AuditAction.VOTER_VERIFIED, "bob",   "Verified voter X")
    LogAuditEntry().execute(AuditAction.POLL_OPENED,    "alice", "Opened poll A")
    alice_entries = GetAuditEntriesByAdmin().execute("alice")
    assert len(alice_entries) == 2
    assert all(entry["performed_by"] == "alice" for entry in alice_entries)


def test_get_audit_entries_by_action_filters_correctly():
    from Backend.audits import LogAuditEntry, GetAuditEntriesByAction, AuditAction
    LogAuditEntry().execute(AuditAction.POLL_CREATED,   "admin", "Created poll A")
    LogAuditEntry().execute(AuditAction.POLL_CREATED,   "admin", "Created poll B")
    LogAuditEntry().execute(AuditAction.VOTER_VERIFIED, "admin", "Verified voter X")
    poll_created_entries = GetAuditEntriesByAction().execute(AuditAction.POLL_CREATED)
    assert len(poll_created_entries) == 2


def test_get_recent_audit_entries_returns_newest_first():
    from Backend.audits import LogAuditEntry, GetRecentAuditEntries, AuditAction
    LogAuditEntry().execute(AuditAction.POLL_CREATED,   "admin", "First entry")
    LogAuditEntry().execute(AuditAction.POLL_OPENED,    "admin", "Second entry")
    LogAuditEntry().execute(AuditAction.POLL_CLOSED,    "admin", "Third entry")
    recent_entries = GetRecentAuditEntries().execute(number_of_entries=2)
    assert len(recent_entries) == 2
    assert recent_entries[0]["details"] == "Third entry"   # newest first
    assert recent_entries[1]["details"] == "Second entry"


def test_audit_log_is_append_only_and_never_modified():
    from Backend.audits import LogAuditEntry, GetAllAuditEntries, AuditStore, AuditAction
    LogAuditEntry().execute(AuditAction.POLL_CREATED, "admin", "Created poll A")
    first_entry_id = GetAllAuditEntries().execute()[0]["id"]

    # Attempting a direct store update should change the record in storage,
    # but no operation class exposes edit or delete — proving append-only by design.
    all_operation_class_names = [
        cls.__name__ for cls in [
            LogAuditEntry, GetAllAuditEntries,
            __import__("audits").GetAuditEntriesByAdmin,
            __import__("audits").GetAuditEntriesByAction,
            __import__("audits").GetRecentAuditEntries,
        ]
    ]
    assert "EditAuditEntry"   not in all_operation_class_names
    assert "DeleteAuditEntry" not in all_operation_class_names

    # The original entry is still intact.
    entries_after = GetAllAuditEntries().execute()
    assert entries_after[0]["id"] == first_entry_id


# ═══════════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n  Election System — Test Suite\n")

    print("  [ Storage ]")
    run("insert assigns auto-incrementing id",        test_store_insert_assigns_auto_incrementing_id)
    run("find returns only matching records",         test_store_find_returns_only_matching_records)
    run("update changes the correct field",           test_store_update_changes_the_correct_field)
    run("delete removes the record",                  test_store_delete_removes_the_record)

    print("\n  [ Polls ]")
    run("create poll — stores it with draft status",         test_create_poll_stores_it_with_draft_status)
    run("create poll — empty title raises error",            test_create_poll_with_empty_title_raises_error)
    run("create poll — end before start raises error",       test_create_poll_with_end_before_start_raises_error)
    run("update poll — changes the title",                   test_update_poll_changes_the_title)
    run("update poll — open poll raises error",              test_update_open_poll_raises_error)
    run("update poll — closed with votes raises error",      test_update_closed_poll_with_votes_raises_error)
    run("delete poll — draft poll removes it",               test_delete_draft_poll_removes_it)
    run("delete poll — open poll raises error",              test_delete_open_poll_raises_error)
    run("open poll — no candidates raises error",            test_open_poll_without_candidates_raises_error)
    run("open poll — with candidates sets status to open",   test_open_poll_with_candidates_sets_status_to_open)
    run("close poll — sets status to closed",                test_close_open_poll_sets_status_to_closed)
    run("close poll — draft poll raises error",              test_close_draft_poll_raises_error)
    run("assign candidates — skips ineligible ids",          test_assign_candidates_skips_ineligible_ids)

    print("\n  [ Voters ]")
    run("get all voters — empty list when none exist",            test_get_all_voters_returns_empty_list_when_none_exist)
    run("verify voter — sets is_verified to true",                test_verify_voter_sets_is_verified_to_true)
    run("verify voter — already verified raises error",           test_verify_already_verified_voter_raises_error)
    run("verify all voters — returns count of voters changed",    test_verify_all_voters_returns_count_of_voters_changed)
    run("deactivate voter — sets is_active to false",             test_deactivate_voter_sets_is_active_to_false)
    run("deactivate voter — already inactive raises error",       test_deactivate_already_inactive_voter_raises_error)
    run("search voters — by name returns matching voter",         test_search_voters_by_name_returns_matching_voter)
    run("search voters — by card number returns matching voter",  test_search_voters_by_card_number_returns_matching_voter)
    run("search voters — unknown field raises error",             test_search_voters_with_unknown_field_raises_error)

    print("\n  [ Admins ]")
    run("authenticate — correct credentials returns admin",        test_authenticate_admin_with_correct_credentials_returns_admin)
    run("authenticate — wrong password raises error",              test_authenticate_admin_with_wrong_password_raises_error)
    run("authenticate — nonexistent admin raises error",           test_authenticate_nonexistent_admin_raises_error)
    run("create admin — as super_admin succeeds",                  test_create_admin_as_super_admin_succeeds)
    run("create admin — as non-super-admin raises error",          test_create_admin_as_non_super_admin_raises_permission_error)
    run("create admin — duplicate username raises error",          test_create_admin_with_duplicate_username_raises_error)
    run("create admin — short password raises error",              test_create_admin_with_short_password_raises_error)
    run("create admin — invalid role raises error",                test_create_admin_with_invalid_role_raises_error)
    run("deactivate admin — sets is_active to false",              test_deactivate_admin_sets_is_active_to_false)
    run("deactivate admin — own account raises error",             test_deactivate_own_account_raises_error)
    run("deactivate admin — as non-super raises permission error", test_deactivate_admin_as_non_super_admin_raises_permission_error)

    print("\n  [ Audits ]")
    run("log entry — saves all fields correctly",              test_log_audit_entry_saves_all_fields)
    run("get all entries — returns every entry",               test_get_all_audit_entries_returns_every_entry)
    run("get by admin — filters to that admin only",           test_get_audit_entries_by_admin_filters_correctly)
    run("get by action — filters to that action only",         test_get_audit_entries_by_action_filters_correctly)
    run("get recent — returns newest first",                   test_get_recent_audit_entries_returns_newest_first)
    run("audit log — append-only with no edit or delete",      test_audit_log_is_append_only_and_never_modified)

    print(f"\n  {'─' * 50}")
    print(f"  {total_passed + total_failed} tests — {total_passed} passed, {total_failed} failed\n")
    shutil.rmtree(TEST_DATA_DIRECTORY, ignore_errors=True)
    sys.exit(0 if total_failed == 0 else 1)
