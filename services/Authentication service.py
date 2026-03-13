# Handles all login, logout, and voter registration logic.

import storage.state as state
from models.voter import Voter
from utils.helpers import hash_password, generate_voter_card_number, calculate_age, current_timestamp
from utils.logger import audit_logger
from storage.store import save_data
from utils.constants import MIN_VOTER_AGE


def login_admin(username: str, password: str):
    hashed = hash_password(password)

    for admin_id_key, admin in state.admins.items():
        if admin["username"] == username and admin["password"] == hashed:

            # Check if the account is active
            if not admin["is_active"]:
                audit_logger.log("LOGIN_FAILED", username, "Account deactivated")
                return None, "deactivated"

            # Successful login
            state.current_user = admin
            state.current_role = "admin"
            audit_logger.log("LOGIN", username, "Admin login successful")
            return admin, "success"

    # No matching admin found
    audit_logger.log("LOGIN_FAILED", username, "Invalid admin credentials")
    return None, "invalid"


def login_voter(voter_card: str, password: str):
    hashed = hash_password(password)

    for voter_id_key, voter in state.voters.items():
        if voter["voter_card_number"] == voter_card and voter["password"] == hashed:

            # Check if the account is active
            if not voter["is_active"]:
                audit_logger.log("LOGIN_FAILED", voter_card, "Voter account deactivated")
                return None, "deactivated"

            # Check if the voter has been verified by admin
            if not voter["is_verified"]:
                audit_logger.log("LOGIN_FAILED", voter_card, "Voter not verified")
                return None, "unverified"

            # Successful login
            state.current_user = voter
            state.current_role = "voter"
            audit_logger.log("LOGIN", voter_card, "Voter login successful")
            return voter, "success"

    # No matching voter found
    audit_logger.log("LOGIN_FAILED", voter_card, "Invalid voter credentials")
    return None, "invalid"


def logout():
    #Log out the current user by clearing the session.
    if state.current_user:
        user_id = state.current_user.get(
            "username", state.current_user.get("voter_card_number", "unknown")
        )
        audit_logger.log("LOGOUT", user_id, f"{state.current_role} logged out")

    state.current_user = None
    state.current_role = None
    save_data()


def register_voter(form_data: dict):
    #Register a new voter using data collected from the registration form.
    global state

    full_name    = form_data["full_name"]
    national_id  = form_data["national_id"]
    dob_str      = form_data["dob_str"]
    gender       = form_data["gender"]
    address      = form_data["address"]
    phone        = form_data["phone"]
    email        = form_data["email"]
    password     = form_data["password"]
    station_id   = form_data["station_choice"]

    # Check that national ID is not already registered
    for voter_id_key, voter in state.voters.items():
        if voter["national_id"] == national_id:
            return False, "A voter with this National ID already exists.", None

    # Validate date of birth and age
    try:
        age = calculate_age(dob_str)
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD.", None

    if age < MIN_VOTER_AGE:
        return False, f"You must be at least {MIN_VOTER_AGE} years old to register.", None

    # Validate gender
    if gender not in ["M", "F", "OTHER"]:
        return False, "Invalid gender selection.", None

    # Validate station selection
    if station_id not in state.voting_stations or not state.voting_stations[station_id]["is_active"]:
        return False, "Invalid station selection.", None

    # Generate voter card and save voter
    voter_card = generate_voter_card_number()

    state.voters[state.voter_id_counter] = {
        "id":               state.voter_id_counter,
        "full_name":        full_name,
        "national_id":      national_id,
        "date_of_birth":    dob_str,
        "age":              age,
        "gender":           gender,
        "address":          address,
        "phone":            phone,
        "email":            email,
        "password":         hash_password(password),
        "voter_card_number": voter_card,
        "station_id":       station_id,
        "is_verified":      False,
        "is_active":        True,
        "has_voted_in":     [],
        "registered_at":    current_timestamp(),
        "role":             "voter",
    }

    audit_logger.log("REGISTER", full_name, f"New voter registered with card: {voter_card}")
    state.voter_id_counter += 1
    save_data()

    return True, "Registration successful.", voter_card