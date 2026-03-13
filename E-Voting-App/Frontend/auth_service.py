"""
auth_service.py - Authentication and registration using module-level UI functions.
Matches the exact interface of the original e_voting_console_app.py.
"""
import random, string, datetime
from security import hash_password
from ui import (clear_screen, header, subheader, menu_item, prompt, masked_input,
                pause, error, success, warning, info, status_badge)
from colors import *

MIN_VOTER_AGE = 18


def admin_login(db):
    """Returns the admin dict on success, None on failure."""
    clear_screen()
    header("ADMIN LOGIN", THEME_ADMIN)
    print()
    username = prompt("Username: ")
    password = masked_input("Password: ").strip()
    hashed = hash_password(password)
    admins = db.get_all("admins")
    for aid, admin in admins.items():
        if admin["username"] == username and admin["password"] == hashed:
            if not admin["is_active"]:
                error("This account has been deactivated.")
                db.log_action("LOGIN_FAILED", username, "Account deactivated")
                pause(); return None
            db.log_action("LOGIN", username, "Admin login successful")
            print(); success(f"Welcome, {admin['full_name']}!")
            pause(); return admin
    error("Invalid credentials.")
    db.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
    pause(); return None


def voter_login(db):
    """Returns the voter dict on success, None on failure."""
    clear_screen()
    header("VOTER LOGIN", THEME_VOTER)
    print()
    voter_card = prompt("Voter Card Number: ")
    password = masked_input("Password: ").strip()
    hashed = hash_password(password)
    voters = db.get_all("voters")
    for vid, voter in voters.items():
        if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
            if not voter["is_active"]:
                error("This voter account has been deactivated.")
                db.log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                pause(); return None
            if not voter["is_verified"]:
                warning("Your voter registration has not been verified yet.")
                info("Please contact an admin to verify your registration.")
                db.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                pause(); return None
            db.log_action("LOGIN", voter_card, "Voter login successful")
            print(); success(f"Welcome, {voter['full_name']}!")
            pause(); return voter
    error("Invalid voter card number or password.")
    db.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
    pause(); return None


def register_voter(db):
    """Register a new voter account."""
    clear_screen()
    header("VOTER REGISTRATION", THEME_VOTER)
    print()
    full_name = prompt("Full Name: ")
    if not full_name: error("Name cannot be empty."); pause(); return
    national_id = prompt("National ID Number: ")
    if not national_id: error("National ID cannot be empty."); pause(); return
    voters = db.get_all("voters")
    for vid, v in voters.items():
        if v["national_id"] == national_id:
            error("A voter with this National ID already exists."); pause(); return
    dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.datetime.now() - dob).days // 365
        if age < MIN_VOTER_AGE:
            error(f"You must be at least {MIN_VOTER_AGE} years old to register."); pause(); return
    except ValueError:
        error("Invalid date format."); pause(); return
    gender = prompt("Gender (M/F/Other): ").upper()
    if gender not in ["M", "F", "OTHER"]:
        error("Invalid gender selection."); pause(); return
    address = prompt("Residential Address: ")
    phone = prompt("Phone Number: ")
    email = prompt("Email Address: ")
    password = masked_input("Create Password: ").strip()
    if len(password) < 6:
        error("Password must be at least 6 characters."); pause(); return
    confirm = masked_input("Confirm Password: ").strip()
    if password != confirm:
        error("Passwords do not match."); pause(); return
    stations = db.get_all("voting_stations")
    if not stations:
        error("No voting stations available. Contact admin."); pause(); return
    subheader("Available Voting Stations", THEME_VOTER)
    for sid, s in stations.items():
        if s["is_active"]:
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
    try:
        station_choice = int(prompt("\nSelect your voting station ID: "))
        if station_choice not in stations or not stations[station_choice]["is_active"]:
            error("Invalid station selection."); pause(); return
    except ValueError:
        error("Invalid input."); pause(); return
    voter_card = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    voter_id = db.get_next_id("voters")
    voter_record = {
        "id": voter_id, "full_name": full_name, "national_id": national_id,
        "date_of_birth": dob_str, "age": age, "gender": gender, "address": address,
        "phone": phone, "email": email, "password": hash_password(password),
        "voter_card_number": voter_card, "station_id": station_choice,
        "is_verified": False, "is_active": True, "has_voted_in": [],
        "registered_at": str(datetime.datetime.now()), "role": "voter",
    }
    db.insert("voters", voter_id, voter_record)
    db.increment_counter("voters")
    db.log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
    print()
    success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
    warning("IMPORTANT: Save this number! You need it to login.")
    info("Your registration is pending admin verification.")
    pause()