"""Login and registration flow. Returns (logged_in, should_exit)."""

from ui import console
from ui.themes import (
    THEME_LOGIN,
    THEME_ADMIN,
    THEME_VOTER,
    BRIGHT_BLUE,
    RESET,
    DIM,
    BOLD,
    BRIGHT_YELLOW,
)
from services import auth_service, audit_service
from services import voter_service
from services import validation
from data.context import DataContext


def run(ctx: DataContext) -> tuple[bool, bool]:
    """Returns (logged_in: bool, should_exit: bool). If should_exit, caller should exit app."""
    console.clear_screen()
    console.header("E-VOTING SYSTEM", THEME_LOGIN)
    print()
    console.menu_item(1, "Login as Admin", THEME_LOGIN)
    console.menu_item(2, "Login as Voter", THEME_LOGIN)
    console.menu_item(3, "Register as Voter", THEME_LOGIN)
    console.menu_item(4, "Exit", THEME_LOGIN)
    print()
    choice = console.prompt("Enter choice: ")

    if choice == "1":
        console.clear_screen()
        console.header("ADMIN LOGIN", THEME_ADMIN)
        print()
        while True:
            username = console.prompt("Username: ")
            password = console.masked_input("Password: ").strip()
            ok, err = auth_service.login_admin(ctx, username, password)
            if ok:
                break
            audit_service.log_action(ctx, "LOGIN_FAILED", username, err or "Invalid admin credentials")
            console.error(err or "Invalid credentials.")
        audit_service.log_action(ctx, "LOGIN", username, "Admin login successful")
        print()
        console.success(f"Welcome, {auth_service.current_user['full_name']}!")
        console.pause()
        return True, False

    if choice == "2":
        console.clear_screen()
        console.header("VOTER LOGIN", THEME_VOTER)
        print()
        while True:
            voter_card = console.prompt("Voter Card Number: ")
            password = console.masked_input("Password: ").strip()
            ok, err = auth_service.login_voter(ctx, voter_card, password)
            if ok:
                audit_service.log_action(ctx, "LOGIN", voter_card, "Voter login successful")
                print()
                console.success(f"Welcome, {auth_service.current_user['full_name']}!")
                console.pause()
                return True, False
            audit_service.log_action(ctx, "LOGIN_FAILED", voter_card, err or "Invalid voter credentials")
            if err == "not_verified":
                console.warning("Your voter registration has not been verified yet.")
                console.info("Please contact an admin to verify your registration.")
                console.pause()
                return False, False
            console.error(err or "Invalid voter card number or password.")

    if choice == "3":
        _register_voter(ctx)
        return False, False

    if choice == "4":
        print()
        console.info("Goodbye!")
        ok, err = ctx.store.save()
        if ok:
            console.info("Data saved successfully")
        else:
            console.error(f"Error saving data: {err}")
        return False, True

    console.error("Invalid choice.")
    console.pause()
    return False, False


def _station_validator(stations):
    def check(s):
        s = (s or "").strip()
        if not s:
            return False, "Enter a station ID."
        try:
            i = int(s)
            return (i in stations, "Invalid station ID. Enter a number from the list.")
        except ValueError:
            return False, "Enter a valid number."
    return check


def _register_voter(ctx: DataContext):
    console.clear_screen()
    console.header("VOTER REGISTRATION", THEME_VOTER)
    print()
    full_name = console.prompt_until_valid("Full Name: ", lambda s: validation.required_non_empty(s, "Name"))
    national_id = console.prompt_until_valid("National ID Number: ", lambda s: validation.required_non_empty(s, "National ID"))
    dob_str = console.prompt_until_valid("Date of Birth (YYYY-MM-DD): ", validation.validate_voter_dob)
    gender = console.prompt_until_valid("Gender (M/F/Other): ", lambda s: (
        (s or "").strip().upper() in ("M", "F", "OTHER"),
        "Invalid gender. Enter M, F, or Other.",
    )).strip().upper()
    address = console.prompt("Residential Address: ")
    phone = console.prompt_until_valid("Phone Number (or leave empty): ", validation.optional_phone, optional=True)
    email = console.prompt_until_valid("Email Address (or leave empty): ", validation.optional_email, optional=True)
    while True:
        password = console.masked_input("Create Password: ").strip()
        if len(password) < 6:
            console.error("Password must be at least 6 characters.")
            continue
        confirm_password = console.masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            console.error("Passwords do not match.")
            continue
        break
    data = {
        "full_name": full_name,
        "national_id": national_id,
        "date_of_birth": dob_str,
        "gender": gender,
        "address": address,
        "phone": phone,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
    }
    stations = {sid: s for sid, s in ctx.stations.get_all().items() if s.get("is_active")}
    if not stations:
        console.error("No voting stations available. Contact admin.")
        console.pause()
        return
    console.subheader("Available Voting Stations", THEME_VOTER)
    for sid, station in stations.items():
        print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
    station_choice_str = console.prompt_until_valid("\nSelect your voting station ID: ", _station_validator(stations))
    data["station_id"] = int(station_choice_str)
    ok, msg = voter_service.register(ctx, data)
    if not ok:
        console.error(msg)
        console.pause()
        return
    audit_service.log_action(ctx, "REGISTER", full_name, f"New voter registered with card: {msg}")
    print()
    console.success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{msg}{RESET}")
    console.warning("IMPORTANT: Save this number! You need it to login.")
    console.info("Your registration is pending admin verification.")
    ok, _ = ctx.store.save()
    console.pause()
