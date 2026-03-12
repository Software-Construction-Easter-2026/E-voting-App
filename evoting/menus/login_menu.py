from evoting.core.colors import BOLD, BRIGHT_YELLOW, DIM, RESET, THEME_LOGIN, THEME_VOTER
from evoting.ui import console_io, display


def run_login(repo, auth_service):
    console_io.clear_screen()
    display.header("E-VOTING SYSTEM", THEME_LOGIN)
    print()
    display.menu_item(1, "Login as Admin", THEME_LOGIN)
    display.menu_item(2, "Login as Voter", THEME_LOGIN)
    display.menu_item(3, "Register as Voter", THEME_LOGIN)
    display.menu_item(4, "Exit", THEME_LOGIN)
    print()
    choice = console_io.prompt("Enter choice: ")

    if choice == "1":
        return _login_admin(auth_service)
    if choice == "2":
        return _login_voter(auth_service)
    if choice == "3":
        _register_voter(repo, auth_service)
        return False
    if choice == "4":
        print()
        display.info("Goodbye!")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
        raise SystemExit(0)
    display.error("Invalid choice.")
    console_io.pause()
    return False


def _login_admin(auth_service):
    from evoting.core.colors import THEME_ADMIN
    console_io.clear_screen()
    display.header("ADMIN LOGIN", THEME_ADMIN)
    print()
    username = console_io.prompt("Username: ")
    password = console_io.masked_input("Password: ").strip()
    ok, result = auth_service.login_admin(username, password)
    if ok:
        print()
        display.success(f"Welcome, {result['full_name']}!")
        console_io.pause()
        return True
    if result == "deactivated":
        display.error("This account has been deactivated.")
        auth_service._audit.log("LOGIN_FAILED", username, "Account deactivated")
    else:
        display.error("Invalid credentials.")
    console_io.pause()
    return False


def _login_voter(auth_service):
    from evoting.core.colors import THEME_VOTER
    console_io.clear_screen()
    display.header("VOTER LOGIN", THEME_VOTER)
    print()
    voter_card = console_io.prompt("Voter Card Number: ")
    password = console_io.masked_input("Password: ").strip()
    ok, result = auth_service.login_voter(voter_card, password)
    if ok:
        print()
        display.success(f"Welcome, {result['full_name']}!")
        console_io.pause()
        return True
    if result == "deactivated":
        display.error("This voter account has been deactivated.")
        auth_service._audit.log("LOGIN_FAILED", voter_card, "Voter account deactivated")
    elif result == "unverified":
        display.warning("Your voter registration has not been verified yet.")
        display.info("Please contact an admin to verify your registration.")
        auth_service._audit.log("LOGIN_FAILED", voter_card, "Voter not verified")
    else:
        display.error("Invalid voter card number or password.")
    console_io.pause()
    return False


def _register_voter(repo, auth_service):
    from evoting.core.colors import BRIGHT_BLUE, RESET, THEME_VOTER
    from evoting.core.constants import MIN_VOTER_AGE
    console_io.clear_screen()
    display.header("VOTER REGISTRATION", THEME_VOTER)
    print()
    full_name = console_io.prompt("Full Name: ")
    if not full_name:
        display.error("Name cannot be empty.")
        console_io.pause()
        return
    national_id = console_io.prompt("National ID Number: ")
    if not national_id:
        display.error("National ID cannot be empty.")
        console_io.pause()
        return
    dob_str = console_io.prompt("Date of Birth (YYYY-MM-DD): ")
    gender = console_io.prompt("Gender (M/F/Other): ").upper()
    address = console_io.prompt("Residential Address: ")
    phone = console_io.prompt("Phone Number: ")
    email = console_io.prompt("Email Address: ")
    password = console_io.masked_input("Create Password: ").strip()
    confirm_password = console_io.masked_input("Confirm Password: ").strip()
    if not repo.voting_stations:
        display.error("No voting stations available. Contact admin.")
        console_io.pause()
        return
    display.subheader("Available Voting Stations", THEME_VOTER)
    for sid, station in repo.voting_stations.items():
        if station.get("is_active", True):
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
    try:
        station_choice = int(console_io.prompt("\nSelect your voting station ID: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if station_choice not in repo.voting_stations or not repo.voting_stations[station_choice].get("is_active", True):
        display.error("Invalid station selection.")
        console_io.pause()
        return
    data = {
        "full_name": full_name,
        "national_id": national_id,
        "dob_str": dob_str,
        "gender": gender,
        "address": address,
        "phone": phone,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "station_id": station_choice,
    }
    ok, result = auth_service.register_voter(data)
    if not ok:
        if result == "duplicate_national_id":
            display.error("A voter with this National ID already exists.")
        elif result == "invalid_date":
            display.error("Invalid date format.")
        elif result == "underage":
            display.error(f"You must be at least {MIN_VOTER_AGE} years old to register.")
        elif result == "invalid_gender":
            display.error("Invalid gender selection.")
        elif result == "short_password":
            display.error("Password must be at least 6 characters.")
        elif result == "password_mismatch":
            display.error("Passwords do not match.")
        else:
            display.error("Invalid station or data.")
        console_io.pause()
        return
    print()
    display.success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{result['voter_card_number']}{RESET}")
    display.warning("IMPORTANT: Save this number! You need it to login.")
    display.info("Your registration is pending admin verification.")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()
