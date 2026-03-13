# Handles voter verification, deactivation, search and password changes.

import storage.state as state
from utils.helpers import hash_password
from utils.logger import audit_logger
from storage.store import save_data


def get_all_voters() -> dict:
    return state.voters


def get_unverified_voters() -> dict:
    return {voter_id_key: voter for voter_id_key, voter in state.voters.items() if not voter["is_verified"]}


def verify_voter(voter_id: int, verified_by: str):
    if voter_id not in state.voters:
        return False, "Voter not found."

    if state.voters[voter_id]["is_verified"]:
        return False, "This voter is already verified."

    state.voters[voter_id]["is_verified"] = True
    voter_name = state.voters[voter_id]["full_name"]

    audit_logger.log("VERIFY_VOTER", verified_by, f"Verified voter: {voter_name}")
    save_data()
    return True, f"Voter '{voter_name}' verified successfully."


def verify_all_voters(verified_by: str):
    unverified = get_unverified_voters()

    if not unverified:
        return False, "No unverified voters found."

    count = 0
    for voter_id_key in unverified:
        state.voters[voter_id_key]["is_verified"] = True
        count += 1

    audit_logger.log("VERIFY_ALL_VOTERS", verified_by, f"Verified {count} voters")
    save_data()
    return True, f"{count} voters verified successfully."


def deactivate_voter(voter_id: int, deactivated_by: str):
    #Deactivate a voter account by ID.
   
    if voter_id not in state.voters:
        return False, "Voter not found."

    if not state.voters[voter_id]["is_active"]:
        return False, "This voter is already deactivated."

    state.voters[voter_id]["is_active"] = False
    voter_name = state.voters[voter_id]["full_name"]

    audit_logger.log(
        "DEACTIVATE_VOTER", deactivated_by,
        f"Deactivated voter: {voter_name}"
    )
    save_data()
    return True, "Voter deactivated successfully."


def search_voters(search_by: str, search_term) -> list:
    results = []

    if search_by == "name":
        results = [
            voter for voter in state.voters.values()
            if search_term.lower() in voter["full_name"].lower()
        ]

    elif search_by == "card":
        results = [
            voter for voter in state.voters.values()
            if search_term == voter["voter_card_number"]
        ]

    elif search_by == "national_id":
        results = [
            voter for voter in state.voters.values()
            if search_term == voter["national_id"]
        ]

    elif search_by == "station":
        results = [
            voter for voter in state.voters.values()
            if voter["station_id"] == search_term
        ]

    return results


def change_voter_password(voter_id: int, old_password: str, new_password: str):
    #Change a voter's password after verifying the old one.
   
    if voter_id not in state.voters:
        return False, "Voter not found."

    voter = state.voters[voter_id]

    # Verify old password
    if hash_password(old_password) != voter["password"]:
        return False, "Incorrect current password."

    # Validate new password length
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    # Save new password
    voter["password"] = hash_password(new_password)

    # Also update current session user if it's the same voter
    if state.current_user and state.current_user.get("id") == voter_id:
        state.current_user["password"] = hash_password(new_password)

    audit_logger.log(
        "CHANGE_PASSWORD",
        voter["voter_card_number"],
        "Password changed"
    )
    save_data()
    return True, "Password changed successfully."