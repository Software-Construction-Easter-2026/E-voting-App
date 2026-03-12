"""Admin dashboard: menu loop and all admin feature handlers."""

from ui import console
from ui.themes import (
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    GREEN,
    YELLOW,
    RED,
    DIM,
    BOLD,
    GRAY,
    BG_GREEN,
    BLACK,
)
from services import auth_service, audit_service
from services import candidate_service, station_service, position_service, poll_service
from services import voter_service, admin_service, voting_service
from services import validation
from models.constants import REQUIRED_EDUCATION_LEVELS, MIN_CANDIDATE_AGE
from data.context import DataContext
import datetime

def _required(prompt_text, field_name=None):
    """
    Forces user to enter a non-empty value.
    If field_name is not provided, it uses the prompt text.
    """
    if field_name is None:
        field_name = prompt_text.replace(":", "").strip()

    return console.prompt_until_valid(
        prompt_text,
        lambda s: validation.required_non_empty(s, field_name)
    )

def run(ctx: DataContext):
    while True:
        console.clear_screen()
        console.header("ADMIN DASHBOARD", THEME_ADMIN)
        user = auth_service.current_user
        print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{user['full_name']}{RESET}  {DIM}│  Role: {user['role']}{RESET}")

        console.subheader("Candidate Management", THEME_ADMIN_ACCENT)
        for i, (num, text) in enumerate([
            (1, "Create Candidate"), (2, "View All Candidates"), (3, "Update Candidate"),
            (4, "Delete Candidate"), (5, "Search Candidates"),
        ], 1):
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("Voting Station Management", THEME_ADMIN_ACCENT)
        for num, text in [(6, "Create Voting Station"), (7, "View All Stations"), (8, "Update Station"), (9, "Delete Station")]:
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("Polls & Positions", THEME_ADMIN_ACCENT)
        for num, text in [
            (10, "Create Position"), (11, "View Positions"), (12, "Update Position"), (13, "Delete Position"),
            (14, "Create Poll"), (15, "View All Polls"), (16, "Update Poll"), (17, "Delete Poll"),
            (18, "Open/Close Poll"), (19, "Assign Candidates to Poll"),
        ]:
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("Voter Management", THEME_ADMIN_ACCENT)
        for num, text in [(20, "View All Voters"), (21, "Verify Voter"), (22, "Deactivate Voter"), (23, "Search Voters")]:
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("Admin Management", THEME_ADMIN_ACCENT)
        for num, text in [(24, "Create Admin Account"), (25, "View Admins"), (26, "Deactivate Admin")]:
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("Results & Reports", THEME_ADMIN_ACCENT)
        for num, text in [(27, "View Poll Results"), (28, "View Detailed Statistics"), (29, "View Audit Log"), (30, "Station-wise Results")]:
            console.menu_item(num, text, THEME_ADMIN)
        console.subheader("System", THEME_ADMIN_ACCENT)
        console.menu_item(31, "Save Data", THEME_ADMIN)
        console.menu_item(32, "Logout", THEME_ADMIN)
        print()
        choice = _required("Enter choice: ")

        handlers = {
            "1": lambda: _create_candidate(ctx),
            "2": lambda: _view_all_candidates(ctx),
            "3": lambda: _update_candidate(ctx),
            "4": lambda: _delete_candidate(ctx),
            "5": lambda: _search_candidates(ctx),
            "6": lambda: _create_station(ctx),
            "7": lambda: _view_all_stations(ctx),
            "8": lambda: _update_station(ctx),
            "9": lambda: _delete_station(ctx),
            "10": lambda: _create_position(ctx),
            "11": lambda: _view_positions(ctx),
            "12": lambda: _update_position(ctx),
            "13": lambda: _delete_position(ctx),
            "14": lambda: _create_poll(ctx),
            "15": lambda: _view_all_polls(ctx),
            "16": lambda: _update_poll(ctx),
            "17": lambda: _delete_poll(ctx),
            "18": lambda: _open_close_poll(ctx),
            "19": lambda: _assign_candidates_to_poll(ctx),
            "20": lambda: _view_all_voters(ctx),
            "21": lambda: _verify_voter(ctx),
            "22": lambda: _deactivate_voter(ctx),
            "23": lambda: _search_voters(ctx),
            "24": lambda: _create_admin(ctx),
            "25": lambda: _view_admins(ctx),
            "26": lambda: _deactivate_admin(ctx),
            "27": lambda: _view_poll_results(ctx),
            "28": lambda: _view_detailed_statistics(ctx),
            "29": lambda: _view_audit_log(ctx),
            "30": lambda: _station_wise_results(ctx),
        }
        if choice == "31":
            ok, err = ctx.store.save()
            if ok:
                console.info("Data saved successfully")
            else:
                console.error(f"Error saving data: {err}")
            console.pause()
        elif choice == "32":
            audit_service.log_action(ctx, "LOGOUT", user["username"], "Admin logged out")
            ctx.store.save()
            auth_service.clear_session()
            return
        elif choice in handlers:
            handlers[choice]()
        else:
            console.error("Invalid choice.")
            console.pause()


RESET = "\033[0m"


def _education_validator():
    n = len(REQUIRED_EDUCATION_LEVELS)
    def check(s):
        s = (s or "").strip()
        if not s:
            return False, "Select an education level (1–{}).".format(n)
        try:
            i = int(s)
            return (1 <= i <= n, "Invalid choice. Enter 1 to {}.".format(n))
        except ValueError:
            return False, "Enter a number from 1 to {}.".format(n)
    return check


def _create_candidate(ctx: DataContext):
    console.clear_screen()
    console.header("CREATE NEW CANDIDATE", THEME_ADMIN)
    print()
    full_name = console.prompt_until_valid("Full Name: ", lambda s: validation.required_non_empty(s, "Name"))
    national_id = console.prompt_until_valid("National ID: ", lambda s: validation.required_non_empty(s, "National ID"))
    dob_str = console.prompt_until_valid("Date of Birth (YYYY-MM-DD): ", validation.validate_candidate_dob)
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    age = (datetime.datetime.now() - dob).days // 365
    gender = console.prompt_until_valid("Gender (M/F/Other): ", lambda s: (
        (s or "").strip().upper() in ("M", "F", "OTHER"),
        "Invalid gender. Enter M, F, or Other.",
    )).strip().upper()
    console.subheader("Education Levels", THEME_ADMIN_ACCENT)
    for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
        print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
    edu_choice_str = console.prompt_until_valid("Select education level: ", _education_validator())
    education = REQUIRED_EDUCATION_LEVELS[int(edu_choice_str) - 1]
    party = _required("Political Party/Affiliation: ")
    manifesto = _required("Brief Manifesto/Bio: ")
    address = _required("Address: ")
    phone = console.prompt_until_valid(
        "Phone (07XXXXXXXX): ",
        validation.validate_phone
    )

    email = console.prompt_until_valid(
        "Email (e.g. name@example.com): ",
        validation.validate_email
    )
    criminal_record = console.prompt_until_valid("Has Criminal Record? (yes/no): ", lambda s: (
        (s or "").strip().lower() in ("yes", "no"),
        "Enter yes or no.",
    )).strip().lower()
    if criminal_record == "yes":
        console.error("Candidates with criminal records are not eligible.")
        audit_service.log_action(ctx, "CANDIDATE_REJECTED", auth_service.current_user["username"], f"Candidate {full_name} rejected - criminal record")
        console.pause()
        return
    years_exp_str = _required("Years of Public Service/Political Experience: ")
    try:
        years_experience = int(years_exp_str)
    except ValueError:
        years_experience = 0
    data = {
        "full_name": full_name,
        "national_id": national_id,
        "date_of_birth": dob_str,
        "age": age,
        "gender": gender,
        "education": education,
        "party": party,
        "manifesto": manifesto,
        "address": address,
        "phone": phone,
        "email": email,
        "has_criminal_record": False,
        "years_experience": years_experience,
    }
    ok, result = candidate_service.create(ctx, data)
    if not ok:
        console.error(result)
        console.pause()
        return
    cid = int(result)
    audit_service.log_action(ctx, "CREATE_CANDIDATE", auth_service.current_user["username"], f"Created candidate: {full_name} (ID: {cid})")
    print()
    console.success(f"Candidate '{full_name}' created successfully! ID: {cid}")
    ctx.store.save()
    console.pause()


def _view_all_candidates(ctx: DataContext):
    console.clear_screen()
    console.header("ALL CANDIDATES", THEME_ADMIN)
    candidates = candidate_service.get_all(ctx)
    if not candidates:
        print()
        console.info("No candidates found.")
        console.pause()
        return
    print()
    console.table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
    console.table_divider(85, THEME_ADMIN)
    for cid, c in candidates.items():
        status = console.status_badge("Active", True) if c.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
    print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
    console.pause()


def _update_candidate(ctx: DataContext):
    console.clear_screen()
    console.header("UPDATE CANDIDATE", THEME_ADMIN)
    candidates = candidate_service.get_all(ctx)
    if not candidates:
        print()
        console.info("No candidates found.")
        console.pause()
        return
    print()
    for cid, c in candidates.items():
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
    try:
        cid = int(_required("\nEnter Candidate ID to update: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    c = candidate_service.get_by_id(ctx, cid)
    if not c:
        console.error("Candidate not found.")
        console.pause()
        return
    print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
    console.info("Press Enter to keep current value\n")
    new_name = console.prompt(f"Full Name [{c['full_name']}]: ")
    if new_name:
        c["full_name"] = new_name
    new_party = console.prompt(f"Party [{c['party']}]: ")
    if new_party:
        c["party"] = new_party
    new_manifesto = console.prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
    if new_manifesto:
        c["manifesto"] = new_manifesto
    new_phone = console.prompt(f"Phone [{c['phone']}]: ")
    if new_phone:
        c["phone"] = new_phone
    new_email = console.prompt(f"Email [{c['email']}]: ")
    if new_email:
        c["email"] = new_email
    new_address = console.prompt(f"Address [{c['address']}]: ")
    if new_address:
        c["address"] = new_address
    new_exp = console.prompt(f"Years Experience [{c['years_experience']}]: ")
    if new_exp:
        try:
            c["years_experience"] = int(new_exp)
        except ValueError:
            console.warning("Invalid number, keeping old value.")
    audit_service.log_action(ctx, "UPDATE_CANDIDATE", auth_service.current_user["username"], f"Updated candidate: {c['full_name']} (ID: {cid})")
    print()
    console.success(f"Candidate '{c['full_name']}' updated successfully!")
    ctx.store.save()
    console.pause()


def _delete_candidate(ctx: DataContext):
    console.clear_screen()
    console.header("DELETE CANDIDATE", THEME_ADMIN)
    candidates = candidate_service.get_all(ctx)
    if not candidates:
        print()
        console.info("No candidates found.")
        console.pause()
        return
    print()
    for cid, c in candidates.items():
        status = console.status_badge("Active", True) if c.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
    try:
        cid = int(_required("\nEnter Candidate ID to delete: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    can_do, err = candidate_service.can_delete(ctx, cid)
    if not can_do:
        console.error(err)
        console.pause()
        return
    c = candidate_service.get_by_id(ctx, cid)
    if not c:
        console.error("Candidate not found.")
        console.pause()
        return
    confirm = console.prompt(f"Are you sure you want to delete '{c['full_name']}'? (yes/no): ").lower()
    if confirm == "yes":
        candidate_service.deactivate(ctx, cid)
        audit_service.log_action(ctx, "DELETE_CANDIDATE", auth_service.current_user["username"], f"Deactivated candidate: {c['full_name']} (ID: {cid})")
        print()
        console.success(f"Candidate '{c['full_name']}' has been deactivated.")
        ctx.store.save()
    else:
        console.info("Deletion cancelled.")
    console.pause()


def _search_candidates(ctx: DataContext):
    console.clear_screen()
    console.header("SEARCH CANDIDATES", THEME_ADMIN)
    console.subheader("Search by", THEME_ADMIN_ACCENT)
    console.menu_item(1, "Name", THEME_ADMIN)
    console.menu_item(2, "Party", THEME_ADMIN)
    console.menu_item(3, "Education Level", THEME_ADMIN)
    console.menu_item(4, "Age Range", THEME_ADMIN)
    choice = _required("\nChoice: ")
    results = []
    if choice == "1":
        term = _required("Enter name to search: ")
        results = candidate_service.search_by_name(ctx, term)
    elif choice == "2":
        term = _required("Enter party name: ")
        results = candidate_service.search_by_party(ctx, term)
    elif choice == "3":
        console.subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(_required("Select: "))
            edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
            results = candidate_service.search_by_education(ctx, edu)
        except (ValueError, IndexError):
            console.error("Invalid choice.")
            console.pause()
            return
    elif choice == "4":
        try:
            min_age = int(_required("Min age: "))
            max_age = int(_required("Max age: "))
            results = candidate_service.search_by_age_range(ctx, min_age, max_age)
        except ValueError:
            console.error("Invalid input.")
            console.pause()
            return
    else:
        console.error("Invalid choice.")
        console.pause()
        return
    if not results:
        print()
        console.info("No candidates found matching your criteria.")
    else:
        print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
        console.table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
        console.table_divider(75, THEME_ADMIN)
        for c in results:
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
    console.pause()


def _capacity_validator(s):
    s = (s or "").strip()
    if not s:
        return False, "Voter capacity is required."
    try:
        i = int(s)
        return (i > 0, "Capacity must be a positive number.")
    except ValueError:
        return False, "Enter a valid number."


def _create_station(ctx: DataContext):
    console.clear_screen()
    console.header("CREATE VOTING STATION", THEME_ADMIN)
    print()
    name = console.prompt_until_valid("Station Name: ", lambda s: validation.required_non_empty(s, "Station name"))
    location = console.prompt_until_valid("Location/Address: ", lambda s: validation.required_non_empty(s, "Location"))
    region = _required("Region/District: ")
    capacity_str = console.prompt_until_valid("Voter Capacity: ", _capacity_validator)
    capacity = int(capacity_str)
    supervisor = _required("Station Supervisor Name: ")
    contact = console.prompt_until_valid(
        "Contact Phone (07XXXXXXXX): ",
        validation.validate_phone
    )
    opening_time = _required("Opening Time (e.g. 08:00): ")
    closing_time = _required("Closing Time (e.g. 17:00): ")
    data = {
        "name": name,
        "location": location,
        "region": region,
        "capacity": capacity,
        "supervisor": supervisor,
        "contact": contact,
        "opening_time": opening_time,
        "closing_time": closing_time,
    }
    ok, result = station_service.create(ctx, data)
    if not ok:
        console.error(result)
        console.pause()
        return
    sid = int(result)
    audit_service.log_action(ctx, "CREATE_STATION", auth_service.current_user["username"], f"Created station: {name} (ID: {sid})")
    print()
    console.success(f"Voting Station '{name}' created! ID: {sid}")
    ctx.store.save()
    console.pause()


def _view_all_stations(ctx: DataContext):
    console.clear_screen()
    console.header("ALL VOTING STATIONS", THEME_ADMIN)
    stations = station_service.get_all(ctx)
    if not stations:
        print()
        console.info("No voting stations found.")
        console.pause()
        return
    print()
    console.table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
    console.table_divider(96, THEME_ADMIN)
    for sid, s in stations.items():
        reg_count = station_service.count_voters_at_station(ctx, sid)
        status = console.status_badge("Active", True) if s.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")
    print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
    console.pause()


def _update_station(ctx: DataContext):
    console.clear_screen()
    console.header("UPDATE VOTING STATION", THEME_ADMIN)
    stations = station_service.get_all(ctx)
    if not stations:
        print()
        console.info("No stations found.")
        console.pause()
        return
    print()
    for sid, s in stations.items():
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
    try:
        sid = int(_required("\nEnter Station ID to update: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    s = station_service.get_by_id(ctx, sid)
    if not s:
        console.error("Station not found.")
        console.pause()
        return
    print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
    console.info("Press Enter to keep current value\n")
    updates = {}
    new_name = console.prompt(f"Name [{s['name']}]: ")
    if new_name:
        updates["name"] = new_name
    new_location = console.prompt(f"Location [{s['location']}]: ")
    if new_location:
        updates["location"] = new_location
    new_region = console.prompt(f"Region [{s['region']}]: ")
    if new_region:
        updates["region"] = new_region
    new_capacity = console.prompt(f"Capacity [{s['capacity']}]: ")
    if new_capacity:
        try:
            updates["capacity"] = int(new_capacity)
        except ValueError:
            console.warning("Invalid number, keeping old value.")
    new_supervisor = console.prompt(f"Supervisor [{s['supervisor']}]: ")
    if new_supervisor:
        updates["supervisor"] = new_supervisor
    new_contact = console.prompt(f"Contact [{s['contact']}]: ")
    if new_contact:
        updates["contact"] = new_contact
    station_service.update(ctx, sid, updates)
    audit_service.log_action(ctx, "UPDATE_STATION", auth_service.current_user["username"], f"Updated station: {s['name']} (ID: {sid})")
    print()
    console.success(f"Station '{s['name']}' updated successfully!")
    ctx.store.save()
    console.pause()


def _delete_station(ctx: DataContext):
    console.clear_screen()
    console.header("DELETE VOTING STATION", THEME_ADMIN)
    stations = station_service.get_all(ctx)
    if not stations:
        print()
        console.info("No stations found.")
        console.pause()
        return
    print()
    for sid, s in stations.items():
        status = console.status_badge("Active", True) if s.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
    try:
        sid = int(_required("\nEnter Station ID to delete: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    s = station_service.get_by_id(ctx, sid)
    if not s:
        console.error("Station not found.")
        console.pause()
        return
    voter_count = station_service.count_voters_at_station(ctx, sid)
    if voter_count > 0:
        console.warning(f"{voter_count} voters are registered at this station.")
        if _required("Proceed with deactivation? (yes/no): ").lower() != "yes":
            console.info("Cancelled.")
            console.pause()
            return
    if console.prompt(f"Confirm deactivation of '{s['name']}'? (yes/no): ").lower() == "yes":
        station_service.deactivate(ctx, sid)
        audit_service.log_action(ctx, "DELETE_STATION", auth_service.current_user["username"], f"Deactivated station: {s['name']}")
        print()
        console.success(f"Station '{s['name']}' deactivated.")
        ctx.store.save()
    else:
        console.info("Cancelled.")
    console.pause()


def _create_position(ctx: DataContext):
    console.clear_screen()
    console.header("CREATE POSITION", THEME_ADMIN)
    print()

    # Title validation
    title = console.prompt_until_valid(
        "Position Title (e.g. President, Governor, Senator): ",
        lambda s: (
            (s or "").strip() != "" and len((s or "").strip()) >= 5,
            "Position title must be at least 5 characters."
        )
    ).strip().title()

    # Description validation
    description = console.prompt_until_valid(
        "Description: ",
        lambda s: validation.required_non_empty(s, "Description")
    )

    # Level validation
    level = console.prompt_until_valid(
        "Level (National/Regional/Local): ",
        lambda s: (
            (s or "").strip().lower() in ("national", "regional", "local"),
            "Invalid level. Enter National, Regional, or Local."
        )
    ).strip().capitalize()

    # Seats validation
    max_winners = int(console.prompt_until_valid(
        "Number of winners/seats (1-10): ",
        lambda s: (
            s.isdigit() and 1 <= int(s) <= 10,
            "Enter a number between 1 and 10."
        )
    ))

    # Minimum candidate age validation
    min_cand_age_str = console.prompt_until_valid(
        f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ",
        lambda s: (
            s == "" or (s.isdigit() and 18 <= int(s) <= 100),
            "Enter a valid age between 18 and 100 or press Enter for default."
        )
    )

    min_cand_age = int(min_cand_age_str) if min_cand_age_str else MIN_CANDIDATE_AGE

    data = {
        "title": title,
        "description": description,
        "level": level,
        "max_winners": max_winners,
        "min_candidate_age": min_cand_age,
    }

    ok, result = position_service.create(ctx, data)

    if not ok:
        console.error(result)
        console.pause()
        return

    pid = int(result)

    audit_service.log_action(
        ctx,
        "CREATE_POSITION",
        auth_service.current_user["username"],
        f"Created position: {title} (ID: {pid})"
    )

    print()
    console.success(f"Position '{title}' created! ID: {pid}")

    ctx.store.save()
    console.pause()

def _view_positions(ctx: DataContext):
    console.clear_screen()
    console.header("ALL POSITIONS", THEME_ADMIN)
    positions = position_service.get_all(ctx)
    if not positions:
        print()
        console.info("No positions found.")
        console.pause()
        return
    print()
    console.table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
    console.table_divider(70, THEME_ADMIN)
    for pid, p in positions.items():
        status = console.status_badge("Active", True) if p.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")
    print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
    console.pause()


def _update_position(ctx: DataContext):
    console.clear_screen()
    console.header("UPDATE POSITION", THEME_ADMIN)
    positions = position_service.get_all(ctx)
    if not positions:
        print()
        console.info("No positions found.")
        console.pause()
        return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try:
        pid = int(_required("\nEnter Position ID to update: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    p = position_service.get_by_id(ctx, pid)
    if not p:
        console.error("Position not found.")
        console.pause()
        return
    print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
    console.info("Press Enter to keep current value\n")
    updates = {}
    new_title = console.prompt(f"Title [{p['title']}]: ")
    if new_title:
        updates["title"] = new_title
    new_desc = console.prompt(f"Description [{p['description'][:50]}]: ")
    if new_desc:
        updates["description"] = new_desc
    new_level = console.prompt(f"Level [{p['level']}]: ")
    if new_level and new_level.lower() in ("national", "regional", "local"):
        updates["level"] = new_level.capitalize()
    new_seats = console.prompt(f"Seats [{p['max_winners']}]: ")
    if new_seats:
        try:
            updates["max_winners"] = int(new_seats)
        except ValueError:
            console.warning("Keeping old value.")
    position_service.update(ctx, pid, updates)
    audit_service.log_action(ctx, "UPDATE_POSITION", auth_service.current_user["username"], f"Updated position: {p['title']}")
    print()
    console.success("Position updated!")
    ctx.store.save()
    console.pause()


def _delete_position(ctx: DataContext):
    console.clear_screen()
    console.header("DELETE POSITION", THEME_ADMIN)
    positions = position_service.get_all(ctx)
    if not positions:
        print()
        console.info("No positions found.")
        console.pause()
        return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try:
        pid = int(_required("\nEnter Position ID to delete: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    can_do, err = position_service.can_delete(ctx, pid)
    if not can_do:
        console.error(err)
        console.pause()
        return
    p = position_service.get_by_id(ctx, pid)
    if not p:
        console.error("Position not found.")
        console.pause()
        return
    if console.prompt(f"Confirm deactivation of '{p['title']}'? (yes/no): ").lower() == "yes":
        position_service.deactivate(ctx, pid)
        audit_service.log_action(ctx, "DELETE_POSITION", auth_service.current_user["username"], f"Deactivated position: {p['title']}")
        print()
        console.success("Position deactivated.")
        ctx.store.save()
    console.pause()


def _create_poll(ctx: DataContext):
    console.clear_screen()
    console.header("CREATE POLL / ELECTION", THEME_ADMIN)
    print()
    title = console.prompt_until_valid("Poll/Election Title: ", lambda s: validation.required_non_empty(s, "Title"))
    description = _required("Description: ")
    election_type = _required("Election Type (General/Primary/By-election/Referendum): ")
    start_date = console.prompt_until_valid(
        "Start Date (YYYY-MM-DD): ",
        lambda s: validation.validate_date(s, allow_future=True)
    )

    while True:
        end_date = console.prompt_until_valid(
            "End Date (YYYY-MM-DD): ",
            lambda s: validation.validate_date(s, allow_future=True)
        )

        sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        if ed <= sd:
            console.error("End date must be after start date.")
        else:
            break
        
    positions = position_service.get_all(ctx)
    active_positions = {pid: p for pid, p in positions.items() if p.get("is_active")}
    if not active_positions:
        console.error("No active positions.")
        console.pause()
        return
    console.subheader("Available Positions", THEME_ADMIN_ACCENT)
    for pid, p in active_positions.items():
        print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
    try:
        selected_position_ids = [int(x.strip()) for x in _required("\nEnter Position IDs (comma-separated): ").split(",")]
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    station_ids = []
    active_stations = {sid: s for sid, s in station_service.get_all(ctx).items() if s.get("is_active")}
    if not active_stations:
        console.error("No voting stations. Create stations first.")
        console.pause()
        return
    console.subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
    for sid, s in active_stations.items():
        print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
    if _required("\nUse all active stations? (yes/no): ").lower() == "yes":
        selected_station_ids = list(active_stations.keys())
    else:
        try:
            selected_station_ids = [int(x.strip()) for x in _required("Enter Station IDs (comma-separated): ").split(",")]
        except ValueError:
            console.error("Invalid input.")
            console.pause()
            return
    data = {
        "title": title,
        "description": description,
        "election_type": election_type,
        "start_date": start_date,
        "end_date": end_date,
        "position_ids": [pid for pid in selected_position_ids if pid in active_positions],
        "station_ids": [sid for sid in selected_station_ids if sid in active_stations],
    }
    if not data["position_ids"]:
        console.error("No valid positions selected.")
        console.pause()
        return
    if not data["station_ids"]:
        console.error("No valid stations selected.")
        console.pause()
        return
    while True:
        ok, result = poll_service.create(ctx, data)
        if ok:
            break
        if "after start" in (result or "").lower():
            console.error(result)
            data["end_date"] = console.prompt_until_valid("End Date (YYYY-MM-DD): ", lambda s: validation.validate_date(s, allow_future=True))
        else:
            console.error(result)
            console.pause()
            return
    pid = int(result)
    audit_service.log_action(ctx, "CREATE_POLL", auth_service.current_user["username"], f"Created poll: {title} (ID: {pid})")
    print()
    console.success(f"Poll '{title}' created! ID: {pid}")
    console.warning("Status: DRAFT - Assign candidates and then open the poll.")
    ctx.store.save()
    console.pause()


def _view_all_polls(ctx: DataContext):
    console.clear_screen()
    console.header("ALL POLLS / ELECTIONS", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        console.info("No polls found.")
        console.pause()
        return
    candidates = candidate_service.get_all(ctx)
    for pid, poll in polls.items():
        sc = GREEN if poll.get("status") == "open" else (YELLOW if poll.get("status") == "draft" else RED)
        print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
        print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll.get("positions", []):
            cand_names = [candidates[ccid]["full_name"] for ccid in pos.get("candidate_ids", []) if ccid in candidates]
            cand_display = ", ".join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
            print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
    print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
    console.pause()


def _update_poll(ctx: DataContext):
    console.clear_screen()
    console.header("UPDATE POLL", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll.get("status") == "open" else (YELLOW if poll.get("status") == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try:
        pid = int(_required("\nEnter Poll ID to update: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    poll = poll_service.get_by_id(ctx, pid)
    if not poll:
        console.error("Poll not found.")
        console.pause()
        return
    if poll.get("status") == "open":
        console.error("Cannot update an open poll. Close it first.")
        console.pause()
        return
    if poll.get("status") == "closed" and (poll.get("total_votes_cast") or 0) > 0:
        console.error("Cannot update a poll with votes.")
        console.pause()
        return
    print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
    console.info("Press Enter to keep current value\n")
    updates = {}
    new_title = console.prompt(f"Title [{poll['title']}]: ")
    if new_title:
        updates["title"] = new_title
    new_desc = console.prompt(f"Description [{poll['description'][:50]}]: ")
    if new_desc:
        updates["description"] = new_desc
    new_type = console.prompt(f"Election Type [{poll['election_type']}]: ")
    if new_type:
        updates["election_type"] = new_type
    new_start = console.prompt(f"Start Date [{poll['start_date']}]: ")
    if new_start:
        try:
            datetime.datetime.strptime(new_start, "%Y-%m-%d")
            updates["start_date"] = new_start
        except ValueError:
            console.warning("Invalid date, keeping old value.")
    new_end = console.prompt(f"End Date [{poll['end_date']}]: ")
    if new_end:
        try:
            datetime.datetime.strptime(new_end, "%Y-%m-%d")
            updates["end_date"] = new_end
        except ValueError:
            console.warning("Invalid date, keeping old value.")
    poll_service.update(ctx, pid, updates)
    audit_service.log_action(ctx, "UPDATE_POLL", auth_service.current_user["username"], f"Updated poll: {poll['title']}")
    print()
    console.success("Poll updated!")
    ctx.store.save()
    console.pause()


def _delete_poll(ctx: DataContext):
    console.clear_screen()
    console.header("DELETE POLL", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try:
        pid = int(_required("\nEnter Poll ID to delete: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    poll = poll_service.get_by_id(ctx, pid)
    if not poll:
        console.error("Poll not found.")
        console.pause()
        return
    if poll.get("status") == "open":
        console.error("Cannot delete an open poll. Close it first.")
        console.pause()
        return
    if (poll.get("total_votes_cast") or 0) > 0:
        console.warning(f"This poll has {poll['total_votes_cast']} votes recorded.")
    if console.prompt(f"Confirm deletion of '{poll['title']}'? (yes/no): ").lower() == "yes":
        poll_service.delete(ctx, pid)
        audit_service.log_action(ctx, "DELETE_POLL", auth_service.current_user["username"], f"Deleted poll: {poll['title']}")
        print()
        console.success(f"Poll '{poll['title']}' deleted.")
        ctx.store.save()
    console.pause()


def _open_close_poll(ctx: DataContext):
    console.clear_screen()
    console.header("OPEN / CLOSE POLL", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll.get("status") == "open" else (YELLOW if poll.get("status") == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
    try:
        pid = int(_required("\nEnter Poll ID: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    poll = poll_service.get_by_id(ctx, pid)
    if not poll:
        console.error("Poll not found.")
        console.pause()
        return
    status = poll.get("status")
    if status == "draft":
        if console.prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
            ok, err = poll_service.open_poll(ctx, pid)
            if not ok:
                console.error(err)
                console.pause()
                return
            audit_service.log_action(ctx, "OPEN_POLL", auth_service.current_user["username"], f"Opened poll: {poll['title']}")
            print()
            console.success(f"Poll '{poll['title']}' is now OPEN for voting!")
            ctx.store.save()
    elif status == "open":
        if console.prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
            poll_service.close_poll(ctx, pid)
            audit_service.log_action(ctx, "CLOSE_POLL", auth_service.current_user["username"], f"Closed poll: {poll['title']}")
            print()
            console.success(f"Poll '{poll['title']}' is now CLOSED.")
            ctx.store.save()
    elif status == "closed":
        console.info("This poll is already closed.")
        if _required("Reopen it? (yes/no): ").lower() == "yes":
            poll_service.reopen_poll(ctx, pid)
            audit_service.log_action(ctx, "REOPEN_POLL", auth_service.current_user["username"], f"Reopened poll: {poll['title']}")
            print()
            console.success("Poll reopened!")
            ctx.store.save()
    console.pause()


def _assign_candidates_to_poll(ctx: DataContext):
    console.clear_screen()
    console.header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    if not candidate_service.get_all(ctx):
        print()
        console.info("No candidates found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try:
        pid = int(_required("\nEnter Poll ID: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    poll = poll_service.get_by_id(ctx, pid)
    if not poll:
        console.error("Poll not found.")
        console.pause()
        return
    if poll.get("status") == "open":
        console.error("Cannot modify candidates of an open poll.")
        console.pause()
        return
    candidates = candidate_service.get_all(ctx)
    positions_data = position_service.get_all(ctx)
    for i, pos in enumerate(poll.get("positions", [])):
        console.subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
        current_cands = [f"{ccid}: {candidates[ccid]['full_name']}" for ccid in pos.get("candidate_ids", []) if ccid in candidates]
        if current_cands:
            print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
        else:
            console.info("No candidates assigned yet.")
        pos_data = positions_data.get(pos["position_id"], {})
        min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        active_candidates = {cid: c for cid, c in candidates.items() if c.get("is_active") and c.get("is_approved")}
        eligible = {cid: c for cid, c in active_candidates.items() if c.get("age", 0) >= min_age}
        if not eligible:
            console.info("No eligible candidates found.")
            continue
        console.subheader("Available Candidates", THEME_ADMIN)
        for cid, c in eligible.items():
            marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos.get("candidate_ids", []) else ""
            print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
        if console.prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
            try:
                new_cand_ids = [int(x.strip()) for x in _required("Enter Candidate IDs (comma-separated): ").split(",")]
                valid_ids = [ncid for ncid in new_cand_ids if ncid in eligible]
                for ncid in new_cand_ids:
                    if ncid not in eligible:
                        console.warning(f"Candidate {ncid} not eligible. Skipping.")
                pos["candidate_ids"] = valid_ids
                console.success(f"{len(valid_ids)} candidate(s) assigned.")
            except ValueError:
                console.error("Invalid input. Skipping this position.")
    audit_service.log_action(ctx, "ASSIGN_CANDIDATES", auth_service.current_user["username"], f"Updated candidates for poll: {poll['title']}")
    ctx.store.save()
    console.pause()


def _view_all_voters(ctx: DataContext):
    console.clear_screen()
    console.header("ALL REGISTERED VOTERS", THEME_ADMIN)
    voters = voter_service.get_all(ctx)
    if not voters:
        print()
        console.info("No voters registered.")
        console.pause()
        return
    print()
    console.table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
    console.table_divider(70, THEME_ADMIN)
    for vid, v in voters.items():
        verified = console.status_badge("Yes", True) if v.get("is_verified") else console.status_badge("No", False)
        active = console.status_badge("Yes", True) if v.get("is_active") else console.status_badge("No", False)
        print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
    verified_count = sum(1 for v in voters.values() if v.get("is_verified"))
    unverified_count = len(voters) - verified_count
    print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
    console.pause()


def _verify_voter(ctx: DataContext):
    console.clear_screen()
    console.header("VERIFY VOTER", THEME_ADMIN)
    voters = voter_service.get_all(ctx)
    unverified = {vid: v for vid, v in voters.items() if not v.get("is_verified")}
    if not unverified:
        print()
        console.info("No unverified voters.")
        console.pause()
        return
    console.subheader("Unverified Voters", THEME_ADMIN_ACCENT)
    for vid, v in unverified.items():
        print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
    print()
    console.menu_item(1, "Verify a single voter", THEME_ADMIN)
    console.menu_item(2, "Verify all pending voters", THEME_ADMIN)
    choice = _required("\nChoice: ")
    if choice == "1":
        try:
            vid = int(_required("Enter Voter ID: "))
        except ValueError:
            console.error("Invalid input.")
            console.pause()
            return
        if vid not in voters:
            console.error("Voter not found.")
            console.pause()
            return
        if voters[vid].get("is_verified"):
            console.info("Already verified.")
            console.pause()
            return
        voter_service.verify(ctx, vid)
        audit_service.log_action(ctx, "VERIFY_VOTER", auth_service.current_user["username"], f"Verified voter: {voters[vid]['full_name']}")
        print()
        console.success(f"Voter '{voters[vid]['full_name']}' verified!")
        ctx.store.save()
    elif choice == "2":
        count = voter_service.verify_all(ctx, unverified.keys())
        audit_service.log_action(ctx, "VERIFY_ALL_VOTERS", auth_service.current_user["username"], f"Verified {count} voters")
        print()
        console.success(f"{count} voters verified!")
        ctx.store.save()
    console.pause()


def _deactivate_voter(ctx: DataContext):
    console.clear_screen()
    console.header("DEACTIVATE VOTER", THEME_ADMIN)
    voters = voter_service.get_all(ctx)
    if not voters:
        print()
        console.info("No voters found.")
        console.pause()
        return
    print()
    try:
        vid = int(_required("Enter Voter ID to deactivate: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    v = voter_service.get_by_id(ctx, vid)
    if not v:
        console.error("Voter not found.")
        console.pause()
        return
    if not v.get("is_active"):
        console.info("Already deactivated.")
        console.pause()
        return
    if console.prompt(f"Deactivate '{v['full_name']}'? (yes/no): ").lower() == "yes":
        voter_service.deactivate(ctx, vid)
        audit_service.log_action(ctx, "DEACTIVATE_VOTER", auth_service.current_user["username"], f"Deactivated voter: {v['full_name']}")
        print()
        console.success("Voter deactivated.")
        ctx.store.save()
    console.pause()


def _search_voters(ctx: DataContext):
    console.clear_screen()
    console.header("SEARCH VOTERS", THEME_ADMIN)
    console.subheader("Search by", THEME_ADMIN_ACCENT)
    console.menu_item(1, "Name", THEME_ADMIN)
    console.menu_item(2, "Voter Card Number", THEME_ADMIN)
    console.menu_item(3, "National ID", THEME_ADMIN)
    console.menu_item(4, "Station", THEME_ADMIN)
    choice = _required("\nChoice: ")
    results = []
    if choice == "1":
        term = _required("Name: ")
        results = voter_service.search_by_name(ctx, term)
    elif choice == "2":
        term = _required("Card Number: ")
        results = voter_service.search_by_card(ctx, term)
    elif choice == "3":
        term = _required("National ID: ")
        results = voter_service.search_by_national_id(ctx, term)
    elif choice == "4":
        try:
            sid = int(_required("Station ID: "))
            results = voter_service.search_by_station(ctx, sid)
        except ValueError:
            console.error("Invalid input.")
            console.pause()
            return
    else:
        console.error("Invalid choice.")
        console.pause()
        return
    if not results:
        print()
        console.info("No voters found.")
    else:
        print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
        for v in results:
            verified = console.status_badge("Verified", True) if v.get("is_verified") else console.status_badge("Unverified", False)
            print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
    console.pause()


def _create_admin(ctx: DataContext):
    console.clear_screen()
    console.header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
    if not admin_service.can_create_admin(ctx):
        print()
        console.error("Only super admins can create admin accounts.")
        console.pause()
        return
    print()
    username = console.prompt_until_valid("Username: ", lambda s: validation.required_non_empty(s, "Username"))
    full_name = _required("Full Name: ")
    email = console.prompt_until_valid("Email (or leave empty): ", validation.optional_email)
    while True:
        password = console.masked_input("Password: ").strip()
        if len(password) < 6:
            console.error("Password must be at least 6 characters.")
            continue
        break
    console.subheader("Available Roles", THEME_ADMIN_ACCENT)
    console.menu_item(1, f"super_admin {DIM}─ Full access{RESET}", THEME_ADMIN)
    console.menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}", THEME_ADMIN)
    console.menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
    console.menu_item(4, f"auditor {DIM}─ Read-only access{RESET}", THEME_ADMIN)
    role_choice = console.prompt_until_valid("\nSelect role (1-4): ", lambda s: (
        (s or "").strip() in ("1", "2", "3", "4"),
        "Invalid role. Enter 1, 2, 3, or 4.",
    ))
    role_map = {"1": "super_admin", "2": "election_officer", "3": "station_manager", "4": "auditor"}
    role = role_map[role_choice.strip()]
    data = {"username": username, "full_name": full_name, "email": email, "password": password, "role": role}
    ok, result = admin_service.create_admin(ctx, data)
    if not ok:
        console.error(result)
        console.pause()
        return
    audit_service.log_action(ctx, "CREATE_ADMIN", auth_service.current_user["username"], f"Created admin: {username} (Role: {role})")
    print()
    console.success(f"Admin '{username}' created with role: {role}")
    ctx.store.save()
    console.pause()


def _view_admins(ctx: DataContext):
    console.clear_screen()
    console.header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    print()
    admins = admin_service.get_all(ctx)
    console.table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
    console.table_divider(78, THEME_ADMIN)
    for aid, a in admins.items():
        active = console.status_badge("Yes", True) if a.get("is_active") else console.status_badge("No", False)
        print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    console.pause()


def _deactivate_admin(ctx: DataContext):
    console.clear_screen()
    console.header("DEACTIVATE ADMIN", THEME_ADMIN)
    if not admin_service.can_deactivate_admin(ctx):
        print()
        console.error("Only super admins can deactivate admins.")
        console.pause()
        return
    print()
    admins = admin_service.get_all(ctx)
    for aid, a in admins.items():
        active = console.status_badge("Active", True) if a.get("is_active") else console.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
    try:
        aid = int(_required("\nEnter Admin ID to deactivate: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    ok, err = admin_service.deactivate(ctx, aid)
    if not ok:
        console.error(err)
        console.pause()
        return
    audit_service.log_action(ctx, "DEACTIVATE_ADMIN", auth_service.current_user["username"], f"Deactivated admin: {admins[aid]['username']}")
    print()
    console.success("Admin deactivated.")
    ctx.store.save()
    console.pause()


def _view_poll_results(ctx: DataContext):
    console.clear_screen()
    console.header("POLL RESULTS", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll.get("status") == "open" else (YELLOW if poll.get("status") == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try:
        pid = int(_required("\nEnter Poll ID: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    poll = poll_service.get_by_id(ctx, pid)
    if not poll:
        console.error("Poll not found.")
        console.pause()
        return
    result = voting_service.get_poll_results(ctx, pid)
    if not result:
        console.pause()
        return
    print()
    console.header(f"RESULTS: {poll['title']}", THEME_ADMIN)
    sc = GREEN if poll.get("status") == "open" else RED
    print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll.get('total_votes_cast', 0)}{RESET}")
    total_eligible = voting_service.get_eligible_voters_count(ctx, pid)
    turnout = (poll.get("total_votes_cast", 0) / total_eligible * 100) if total_eligible > 0 else 0
    tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
    print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
    candidates = candidate_service.get_all(ctx)
    for pr in result["positions_result"]:
        pos = pr["position"]
        console.subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
        vote_counts = pr["vote_counts"]
        abstain_count = pr["abstain_count"]
        total_pos = pr["total"]
        for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
            cand = candidates.get(cid, {})
            pct = (count / total_pos * 100) if total_pos > 0 else 0
            bl = int(pct / 2)
            bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
            winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos.get("max_winners", 1) else ""
            print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
            print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
        if abstain_count > 0:
            print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
        if not vote_counts:
            console.info("    No votes recorded for this position.")
    console.pause()


def _view_detailed_statistics(ctx: DataContext):
    console.clear_screen()
    console.header("DETAILED STATISTICS", THEME_ADMIN)
    console.subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
    candidates = candidate_service.get_all(ctx)
    voters = voter_service.get_all(ctx)
    stations = station_service.get_all(ctx)
    polls = poll_service.get_all(ctx)
    tc = len(candidates)
    ac = sum(1 for c in candidates.values() if c.get("is_active"))
    tv = len(voters)
    vv = sum(1 for v in voters.values() if v.get("is_verified"))
    av = sum(1 for v in voters.values() if v.get("is_active"))
    ts = len(stations)
    ast = sum(1 for s in stations.values() if s.get("is_active"))
    tp = len(polls)
    op = sum(1 for p in polls.values() if p.get("status") == "open")
    cp = sum(1 for p in polls.values() if p.get("status") == "closed")
    dp = sum(1 for p in polls.values() if p.get("status") == "draft")
    print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
    print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
    print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
    print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
    print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(ctx.votes.get_all())}")
    console.subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
    gender_counts = {}
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    for v in voters.values():
        g = v.get("gender", "?")
        gender_counts[g] = gender_counts.get(g, 0) + 1
        age = v.get("age", 0)
        if age <= 25:
            age_groups["18-25"] += 1
        elif age <= 35:
            age_groups["26-35"] += 1
        elif age <= 45:
            age_groups["36-45"] += 1
        elif age <= 55:
            age_groups["46-55"] += 1
        elif age <= 65:
            age_groups["56-65"] += 1
        else:
            age_groups["65+"] += 1
    for g, count in gender_counts.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {g}: {count} ({pct:.1f}%)")
    print(f"  {BOLD}Age Distribution:{RESET}")
    for group, count in age_groups.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
    console.subheader("STATION LOAD", THEME_ADMIN_ACCENT)
    for sid, s in stations.items():
        vc = sum(1 for v in voters.values() if v.get("station_id") == sid)
        lp = (vc / s.get("capacity", 1) * 100) if s.get("capacity") else 0
        lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
        st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
        print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
    console.subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
    party_counts = {}
    for c in candidates.values():
        if c.get("is_active"):
            party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
    for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
    console.subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
    edu_counts = {}
    for c in candidates.values():
        if c.get("is_active"):
            edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
    for edu, count in edu_counts.items():
        print(f"    {edu}: {BOLD}{count}{RESET}")
    console.pause()


def _view_audit_log(ctx: DataContext):
    console.clear_screen()
    console.header("AUDIT LOG", THEME_ADMIN)
    audit_log = ctx.audit.get_all()
    if not audit_log:
        print()
        console.info("No audit records.")
        console.pause()
        return
    print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
    console.subheader("Filter", THEME_ADMIN_ACCENT)
    console.menu_item(1, "Last 20 entries", THEME_ADMIN)
    console.menu_item(2, "All entries", THEME_ADMIN)
    console.menu_item(3, "Filter by action type", THEME_ADMIN)
    console.menu_item(4, "Filter by user", THEME_ADMIN)
    choice = _required("\nChoice: ")
    entries = audit_log
    if choice == "1":
        entries = audit_log[-20:]
    elif choice == "3":
        action_types = list(set(e.get("action", "") for e in audit_log))
        for i, at in enumerate(action_types, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
        try:
            at_choice = int(_required("Select action type: "))
            entries = [e for e in audit_log if e.get("action") == action_types[at_choice - 1]]
        except (ValueError, IndexError):
            console.error("Invalid choice.")
            console.pause()
            return
    elif choice == "4":
        uf = _required("Enter username/card number: ")
        entries = [e for e in audit_log if uf.lower() in (e.get("user") or "").lower()]
    print()
    console.table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
    console.table_divider(100, THEME_ADMIN)
    for entry in entries:
        ac = GREEN if "CREATE" in (entry.get("action") or "") or entry.get("action") == "LOGIN" else (
            RED if "DELETE" in (entry.get("action") or "") or "DEACTIVATE" in (entry.get("action") or "") else (
                YELLOW if "UPDATE" in (entry.get("action") or "") else RESET
            )
        )
        ts = (entry.get("timestamp") or "")[:19]
        action = (entry.get("action") or "")[:25].ljust(25)
        user = (entry.get("user") or "")[:20].ljust(20)
        details = (entry.get("details") or "")[:50]
        print(f"  {DIM}{ts}{RESET}  {ac}{action}{RESET} {user} {DIM}{details}{RESET}")
    console.pause()


def _station_wise_results(ctx: DataContext):
    console.clear_screen()
    console.header("STATION-WISE RESULTS", THEME_ADMIN)
    polls = poll_service.get_all(ctx)
    if not polls:
        print()
        console.info("No polls found.")
        console.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll.get("status") == "open" else (YELLOW if poll.get("status") == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try:
        pid = int(_required("\nEnter Poll ID: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    if pid not in polls:
        console.error("Poll not found.")
        console.pause()
        return
    result = voting_service.get_station_wise_results(ctx, pid)
    if not result:
        console.pause()
        return
    poll = result["poll"]
    print()
    console.header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
    candidates = candidate_service.get_all(ctx)
    for sr in result["stations"]:
        station = sr["station"]
        console.subheader(f"{station['name']}  ({station['location']})", "\033[97m")
        ras = sr["registered_at_station"]
        svc = sr["unique_voters"]
        st = sr["turnout_pct"]
        tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
        print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
        for pr in sr["position_results"]:
            pos = pr["position"]
            print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
            vc = pr["vote_counts"]
            ac = pr["abstain_count"]
            total = sum(vc.values()) + ac
            for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
            if ac > 0:
                print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
    console.pause()
