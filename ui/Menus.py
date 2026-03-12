#This file has code to display the menus
import os
import sys

from Display import (
    header, subheader, menu_item, prompt, info, error, success, warning,
    table_header, table_divider, status_badge, masked_input,
    THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER, THEME_VOTER_ACCENT,
    THEME_LOGIN, BOLD, DIM, RESET, GREEN, RED, YELLOW, GRAY,
    BRIGHT_BLUE, BRIGHT_GREEN, BRIGHT_WHITE, BRIGHT_YELLOW, BRIGHT_CYAN,
    ITALIC, BG_GREEN, BLACK
)

def clear_screen():
    #Clear the terminal screen.
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    #Pause execution until the user presses Enter.
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def show_login_menu():
    #Display the main login menu and return the user's choice.
    clear_screen()
    header("E-VOTING SYSTEM", THEME_LOGIN)
    print()
    menu_item(1, "Login as Admin", THEME_LOGIN)
    menu_item(2, "Login as Voter", THEME_LOGIN)
    menu_item(3, "Register as Voter", THEME_LOGIN)
    menu_item(4, "Exit", THEME_LOGIN)
    print()
    return prompt("Enter choice: ")


def show_admin_login_screen():
    #Display the admin login screen and return the username and password.
    clear_screen()
    header("ADMIN LOGIN", THEME_ADMIN)
    print()
    username = prompt("Username: ")
    password = masked_input("Password: ").strip()
    return username, password


def show_voter_login_screen():
    #Display the voter login screen and return the voter card number and password.
    clear_screen()
    header("VOTER LOGIN", THEME_VOTER)
    print()
    voter_card = prompt("Voter Card Number: ")
    password = masked_input("Password: ").strip()
    return voter_card, password


def show_admin_dashboard(current_user):
    #Display the admin dashboard and return the selected menu option.
    clear_screen()
    header("ADMIN DASHBOARD", THEME_ADMIN)
    print(
        f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}"
        f"  {DIM}│  Role: {current_user['role']}{RESET}"
    )

    subheader("Candidate Management", THEME_ADMIN_ACCENT)
    menu_item(1, "Create Candidate", THEME_ADMIN)
    menu_item(2, "View All Candidates", THEME_ADMIN)
    menu_item(3, "Update Candidate", THEME_ADMIN)
    menu_item(4, "Delete Candidate", THEME_ADMIN)
    menu_item(5, "Search Candidates", THEME_ADMIN)

    subheader("Voting Station Management", THEME_ADMIN_ACCENT)
    menu_item(6, "Create Voting Station", THEME_ADMIN)
    menu_item(7, "View All Stations", THEME_ADMIN)
    menu_item(8, "Update Station", THEME_ADMIN)
    menu_item(9, "Delete Station", THEME_ADMIN)

    subheader("Polls & Positions", THEME_ADMIN_ACCENT)
    menu_item(10, "Create Position", THEME_ADMIN)
    menu_item(11, "View Positions", THEME_ADMIN)
    menu_item(12, "Update Position", THEME_ADMIN)
    menu_item(13, "Delete Position", THEME_ADMIN)
    menu_item(14, "Create Poll", THEME_ADMIN)
    menu_item(15, "View All Polls", THEME_ADMIN)
    menu_item(16, "Update Poll", THEME_ADMIN)
    menu_item(17, "Delete Poll", THEME_ADMIN)
    menu_item(18, "Open/Close Poll", THEME_ADMIN)
    menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

    subheader("Voter Management", THEME_ADMIN_ACCENT)
    menu_item(20, "View All Voters", THEME_ADMIN)
    menu_item(21, "Verify Voter", THEME_ADMIN)
    menu_item(22, "Deactivate Voter", THEME_ADMIN)
    menu_item(23, "Search Voters", THEME_ADMIN)

    subheader("Admin Management", THEME_ADMIN_ACCENT)
    menu_item(24, "Create Admin Account", THEME_ADMIN)
    menu_item(25, "View Admins", THEME_ADMIN)
    menu_item(26, "Deactivate Admin", THEME_ADMIN)

    subheader("Results & Reports", THEME_ADMIN_ACCENT)
    menu_item(27, "View Poll Results", THEME_ADMIN)
    menu_item(28, "View Detailed Statistics", THEME_ADMIN)
    menu_item(29, "View Audit Log", THEME_ADMIN)
    menu_item(30, "Station-wise Results", THEME_ADMIN)

    subheader("System", THEME_ADMIN_ACCENT)
    menu_item(31, "Save Data", THEME_ADMIN)
    menu_item(32, "Logout", THEME_ADMIN)

    print()
    return prompt("Enter choice: ")


def show_voter_dashboard(current_user, station_name):
    #Display the voter dashboard and return the selected menu option.
    clear_screen()
    header("VOTER DASHBOARD", THEME_VOTER)
    print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}")
    print(
        f"  {DIM}    Card: {current_user['voter_card_number']}"
        f"  │  Station: {station_name}{RESET}"
    )
    print()
    menu_item(1, "View Open Polls", THEME_VOTER)
    menu_item(2, "Cast Vote", THEME_VOTER)
    menu_item(3, "View My Voting History", THEME_VOTER)
    menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
    menu_item(5, "View My Profile", THEME_VOTER)
    menu_item(6, "Change Password", THEME_VOTER)
    menu_item(7, "Logout", THEME_VOTER)
    print()
    return prompt("Enter choice: ")


def show_voter_registration_form(voting_stations):
    #Display the voter registration form and return the entered details.
    clear_screen()
    header("VOTER REGISTRATION", THEME_VOTER)
    print()

    full_name = prompt("Full Name: ")
    if not full_name:
        error("Name cannot be empty.")
        pause()
        return None

    national_id = prompt("National ID Number: ")
    if not national_id:
        error("National ID cannot be empty.")
        pause()
        return None

    dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
    gender = prompt("Gender (M/F/Other): ").upper()
    address = prompt("Residential Address: ")
    phone = prompt("Phone Number: ")
    email = prompt("Email Address: ")
    password = masked_input("Create Password: ").strip()

    if len(password) < 6:
        error("Password must be at least 6 characters.")
        pause()
        return None

    confirm_password = masked_input("Confirm Password: ").strip()
    if password != confirm_password:
        error("Passwords do not match.")
        pause()
        return None

    if not voting_stations:
        error("No voting stations available. Contact admin.")
        pause()
        return None

    subheader("Available Voting Stations", THEME_VOTER)
    for station_id, station in voting_stations.items():
        if station["is_active"]:
            print(
                f"    {BRIGHT_BLUE}{station_id}.{RESET} {station['name']}"
                f" {DIM}- {station['location']}{RESET}"
            )

    try:
        station_choice = int(prompt("\nSelect your voting station ID: "))
    except ValueError:
        error("Invalid input.")
        pause()
        return None

    return {
        "full_name": full_name,
        "national_id": national_id,
        "dob_str": dob_str,
        "gender": gender,
        "address": address,
        "phone": phone,
        "email": email,
        "password": password,
        "station_choice": station_choice,
    }


def show_voter_registration_success(voter_card):
    #Display a successful voter registration message.
    print()
    success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
    warning("IMPORTANT: Save this number! You need it to login.")
    info("Your registration is pending admin verification.")
    pause()


def show_candidates_table(candidates):
    #Display a table of all candidates
    clear_screen()
    header("ALL CANDIDATES", THEME_ADMIN)

    if not candidates:
        print()
        info("No candidates found.")
        pause()
        return

    print()
    table_header(
        f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}",
        THEME_ADMIN,
    )
    table_divider(85, THEME_ADMIN)

    for candidate in candidates.values():
        status = (
            status_badge("Active", True)
            if candidate["is_active"]
            else status_badge("Inactive", False)
        )
        print(
            f"  {candidate['id']:<5} {candidate['full_name']:<25} "
            f"{candidate['party']:<20} {candidate['age']:<5} "
            f"{candidate['education']:<20} {status}"
        )

    print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
    pause()


def show_candidate_search_menu():
    #Display the candidate search options and return the user's choice.
    clear_screen()
    header("SEARCH CANDIDATES", THEME_ADMIN)
    subheader("Search by", THEME_ADMIN_ACCENT)
    menu_item(1, "Name", THEME_ADMIN)
    menu_item(2, "Party", THEME_ADMIN)
    menu_item(3, "Education Level", THEME_ADMIN)
    menu_item(4, "Age Range", THEME_ADMIN)
    return prompt("\nChoice: ")


def show_stations_table(voting_stations, voters):
    #Display a table of all voting stations.
    clear_screen()
    header("ALL VOTING STATIONS", THEME_ADMIN)

    if not voting_stations:
        print()
        info("No voting stations found.")
        pause()
        return

    print()
    table_header(
        f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
        THEME_ADMIN,
    )
    table_divider(96, THEME_ADMIN)

    for station_id, station in voting_stations.items():
        registered_count = sum(
            1 for voter in voters.values() if voter["station_id"] == station_id
        )
        status = (
            status_badge("Active", True)
            if station["is_active"]
            else status_badge("Inactive", False)
        )
        print(
            f"  {station['id']:<5} {station['name']:<25} {station['location']:<25}"
            f" {station['region']:<15} {station['capacity']:<8} {registered_count:<8} {status}"
        )

    print(f"\n  {DIM}Total Stations: {len(voting_stations)}{RESET}")
    pause()


def show_all_polls(polls, candidates):
    #Display all polls with their positions and assigned candidates.
    clear_screen()
    header("ALL POLLS / ELECTIONS", THEME_ADMIN)

    if not polls:
        print()
        info("No polls found.")
        pause()
        return

    for poll in polls.values():
        status_color = (
            GREEN if poll["status"] == "open"
            else YELLOW if poll["status"] == "draft"
            else RED
        )
        print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
        print(
            f"  {DIM}Type:{RESET} {poll['election_type']}"
            f"  {DIM}│  Status:{RESET} {status_color}{BOLD}{poll['status'].upper()}{RESET}"
        )
        print(
            f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}"
            f"  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}"
        )

        for position in poll["positions"]:
            candidate_names = [
                candidates[candidate_id]["full_name"]
                for candidate_id in position["candidate_ids"]
                if candidate_id in candidates
            ]
            candidate_display = (
                ", ".join(candidate_names)
                if candidate_names
                else f"{DIM}None assigned{RESET}"
            )
            print(
                f"    {THEME_ADMIN_ACCENT}▸{RESET} "
                f"{position['position_title']}: {candidate_display}"
            )

    print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
    pause()


def show_voters_table(voters):
    #Display a table of all registered voters.
    clear_screen()
    header("ALL REGISTERED VOTERS", THEME_ADMIN)

    if not voters:
        print()
        info("No voters registered.")
        pause()
        return

    print()
    table_header(
        f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
        THEME_ADMIN,
    )
    table_divider(70, THEME_ADMIN)

    for voter in voters.values():
        verified_status = (
            status_badge("Yes", True)
            if voter["is_verified"]
            else status_badge("No", False)
        )
        active_status = (
            status_badge("Yes", True)
            if voter["is_active"]
            else status_badge("No", False)
        )
        print(
            f"  {voter['id']:<5} {voter['full_name']:<25} "
            f"{voter['voter_card_number']:<15} {voter['station_id']:<6} "
            f"{verified_status:<19} {active_status}"
        )

    verified_count = sum(1 for voter in voters.values() if voter["is_verified"])
    unverified_count = sum(1 for voter in voters.values() if not voter["is_verified"])
    print(
        f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  "
        f"Unverified: {unverified_count}{RESET}"
    )
    pause()


def show_voter_profile(current_user, voting_stations):
    #Display the currently logged-in voter's full profile.
    clear_screen()
    header("MY PROFILE", THEME_VOTER)
    station_name = voting_stations.get(current_user["station_id"], {}).get(
        "name", "Unknown"
    )
    print()

    fields = [
        ("Name", current_user["full_name"]),
        ("National ID", current_user["national_id"]),
        ("Voter Card", f"{BRIGHT_YELLOW}{current_user['voter_card_number']}{RESET}"),
        ("Date of Birth", current_user["date_of_birth"]),
        ("Age", current_user["age"]),
        ("Gender", current_user["gender"]),
        ("Address", current_user["address"]),
        ("Phone", current_user["phone"]),
        ("Email", current_user["email"]),
        ("Station", station_name),
        (
            "Verified",
            status_badge("Yes", True)
            if current_user["is_verified"]
            else status_badge("No", False),
        ),
        ("Registered", current_user["registered_at"]),
        ("Polls Voted", len(current_user.get("has_voted_in", []))),
    ]

    for label, value in fields:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")

    pause()


def show_results_bar_chart(
    poll,
    votes,
    candidates,
    positions,
    voters,
    theme_color,
    winner_label="★ WINNER",
):
    #Display poll results using a text-based bar chart.
    for position in poll["positions"]:
        max_winners = position.get("max_winners", 1)
        subheader(
            f"{position['position_title']} (Seats: {max_winners})",
            THEME_ADMIN_ACCENT,
        )

        vote_counts = {}
        abstained_count = 0
        total_votes = 0

        for vote in votes:
            if (
                vote["poll_id"] == poll["id"]
                and vote["position_id"] == position["position_id"]
            ):
                total_votes += 1
                if vote["abstained"]:
                    abstained_count += 1
                else:
                    candidate_id = vote["candidate_id"]
                    vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1

        sorted_results = sorted(
            vote_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for rank, (candidate_id, vote_count) in enumerate(sorted_results, start=1):
            candidate = candidates.get(candidate_id, {})
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            filled_blocks = int(percentage / 2)
            bar = (
                f"{theme_color}{'█' * filled_blocks}"
                f"{GRAY}{'░' * (50 - filled_blocks)}{RESET}"
            )
            winner_badge = (
                f" {BG_GREEN}{BLACK}{BOLD} {winner_label} {RESET}"
                if rank <= max_winners
                else ""
            )

            print(
                f"    {BOLD}{rank}. {candidate.get('full_name', '?')}{RESET} "
                f"{DIM}({candidate.get('party', '?')}){RESET}"
            )
            print(
                f"       {bar} {BOLD}{vote_count}{RESET} "
                f"({percentage:.1f}%){winner_badge}"
            )

        if abstained_count > 0:
            abstained_percentage = (
                (abstained_count / total_votes * 100) if total_votes > 0 else 0
            )
            print(
                f"    {GRAY}Abstained: {abstained_count} "
                f"({abstained_percentage:.1f}%){RESET}"
            )

        if not vote_counts:
            info("    No votes recorded for this position.")


def show_admins_table(admins):
    #Display a table of all admin accounts.
    clear_screen()
    header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    print()
    table_header(
        f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
        THEME_ADMIN,
    )
    table_divider(78, THEME_ADMIN)

    for admin in admins.values():
        active_status = (
            status_badge("Yes", True)
            if admin["is_active"]
            else status_badge("No", False)
        )
        print(
            f"  {admin['id']:<5} {admin['username']:<20} "
            f"{admin['full_name']:<25} {admin['role']:<20} {active_status}"
        )

    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    pause()


def show_audit_log_menu():
    #Display audit log filter options and return the user's choice.
    clear_screen()
    header("AUDIT LOG", THEME_ADMIN)
    subheader("Filter", THEME_ADMIN_ACCENT)
    menu_item(1, "Last 20 entries", THEME_ADMIN)
    menu_item(2, "All entries", THEME_ADMIN)
    menu_item(3, "Filter by action type", THEME_ADMIN)
    menu_item(4, "Filter by user", THEME_ADMIN)
    return prompt("\nChoice: ")


def show_audit_entries(entries):
    #Display a formatted table of audit log entries.
    print()
    table_header(
        f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}",
        THEME_ADMIN,
    )
    table_divider(100, THEME_ADMIN)

    for entry in entries:
        if "CREATE" in entry["action"] or entry["action"] == "LOGIN":
            action_color = GREEN
        elif "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]:
            action_color = RED
        elif "UPDATE" in entry["action"]:
            action_color = YELLOW
        else:
            action_color = RESET

        print(
            f"  {DIM}{entry['timestamp'][:19]}{RESET}  "
            f"{action_color}{entry['action']:<25}{RESET} "
            f"{entry['user']:<20} "
            f"{DIM}{entry['details'][:50]}{RESET}"
        )