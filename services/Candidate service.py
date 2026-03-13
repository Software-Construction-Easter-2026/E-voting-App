# Handles creating, viewing, updating, deleting and searching candidates.

import storage.state as state
from utils.helpers import calculate_age, current_timestamp
from utils.logger import audit_logger
from storage.store import save_data
from utils.constants import (
    MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS
)


def create_candidate(form_data: dict):
    #Create a new candidate after validating eligibility.
    full_name        = form_data["full_name"]
    national_id      = form_data["national_id"]
    dob_str          = form_data["dob_str"]
    gender           = form_data["gender"]
    education        = form_data["education"]
    party            = form_data["party"]
    manifesto        = form_data["manifesto"]
    address          = form_data["address"]
    phone            = form_data["phone"]
    email            = form_data["email"]
    criminal_record  = form_data["criminal_record"]
    years_experience = form_data["years_experience"]
    created_by       = form_data["created_by"]

    # Check for duplicate national ID
    for candidate_id_key, candidate in state.candidates.items():
        if candidate["national_id"] == national_id:
            return False, "A candidate with this National ID already exists."

    # Validate age
    try:
        age = calculate_age(dob_str)
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."

    if age < MIN_CANDIDATE_AGE:
        return False, f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"

    if age > MAX_CANDIDATE_AGE:
        return False, f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"

    # Reject candidates with criminal records
    if criminal_record == "yes":
        audit_logger.log(
            "CANDIDATE_REJECTED", created_by,
            f"Candidate {full_name} rejected - criminal record"
        )
        return False, "Candidates with criminal records are not eligible."

    # Save the new candidate
    state.candidates[state.candidate_id_counter] = {
        "id":               state.candidate_id_counter,
        "full_name":        full_name,
        "national_id":      national_id,
        "date_of_birth":    dob_str,
        "age":              age,
        "gender":           gender,
        "education":        education,
        "party":            party,
        "manifesto":        manifesto,
        "address":          address,
        "phone":            phone,
        "email":            email,
        "has_criminal_record": False,
        "years_experience": years_experience,
        "is_active":        True,
        "is_approved":      True,
        "created_at":       current_timestamp(),
        "created_by":       created_by,
    }

    audit_logger.log(
        "CREATE_CANDIDATE", created_by,
        f"Created candidate: {full_name} (ID: {state.candidate_id_counter})"
    )

    state.candidate_id_counter += 1
    save_data()
    return True, f"Candidate '{full_name}' created successfully! ID: {state.candidate_id_counter - 1}"


def get_all_candidates() -> dict:
    return state.candidates


def get_candidate_by_id(candidate_id: int):
    return state.candidates.get(candidate_id)


def update_candidate(candidate_id: int, updates: dict, updated_by: str):
    if candidate_id not in state.candidates:
        return False, "Candidate not found."

    candidate = state.candidates[candidate_id]

    # Apply only the fields that were provided
    updatable_fields = ["full_name", "party", "manifesto", "phone", "email", "address", "years_experience"]
    for field in updatable_fields:
        if field in updates and updates[field]:
            candidate[field] = updates[field]

    audit_logger.log(
        "UPDATE_CANDIDATE", updated_by,
        f"Updated candidate: {candidate['full_name']} (ID: {candidate_id})"
    )
    save_data()
    return True, f"Candidate '{candidate['full_name']}' updated successfully."


def delete_candidate(candidate_id: int, deleted_by: str):
    #Deactivate a candidate by ID.
    if candidate_id not in state.candidates:
        return False, "Candidate not found."

    # Prevent deletion if candidate is in an active poll
    for poll_id_key, poll in state.polls.items():
        if poll["status"] == "open":
            for position in poll.get("positions", []):
                if candidate_id in position.get("candidate_ids", []):
                    return False, f"Cannot delete — candidate is in active poll: {poll['title']}"

    candidate_name = state.candidates[candidate_id]["full_name"]
    state.candidates[candidate_id]["is_active"] = False

    audit_logger.log(
        "DELETE_CANDIDATE", deleted_by,
        f"Deactivated candidate: {candidate_name} (ID: {candidate_id})"
    )
    save_data()
    return True, f"Candidate '{candidate_name}' has been deactivated."


def search_candidates(search_by: str, search_term) -> list:
    results = []

    if search_by == "name":
        results = [
            candidate for candidate in state.candidates.values()
            if search_term.lower() in candidate["full_name"].lower()
        ]

    elif search_by == "party":
        results = [
            candidate for candidate in state.candidates.values()
            if search_term.lower() in candidate["party"].lower()
        ]

    elif search_by == "education":
        results = [
            candidate for candidate in state.candidates.values()
            if candidate["education"] == search_term
        ]

    elif search_by == "age_range":
        min_age, max_age = search_term
        results = [
            candidate for candidate in state.candidates.values()
            if min_age <= candidate["age"] <= max_age
        ]

    return results