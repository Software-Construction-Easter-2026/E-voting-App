from evoting.core.colors import (
    BOLD,
    DIM,
    GREEN,
    RED,
    RESET,
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    YELLOW,
)
from evoting.core.constants import MIN_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS
from evoting.ui import console_io, display


def create_candidate(ctx):
    repo, auth, candidate_svc = ctx.repo, ctx.auth, ctx.candidate_svc
    console_io.clear_screen()
    display.header("CREATE NEW CANDIDATE", THEME_ADMIN)
    print()
    full_name = console_io.prompt("Full Name: ")
    if not full_name:
        display.error("Name cannot be empty.")
        console_io.pause()
        return
    national_id = console_io.prompt("National ID: ")
    if not national_id:
        display.error("National ID cannot be empty.")
        console_io.pause()
        return
    dob_str = console_io.prompt("Date of Birth (YYYY-MM-DD): ")
    gender = console_io.prompt("Gender (M/F/Other): ").upper()
    display.subheader("Education Levels", THEME_ADMIN_ACCENT)
    for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
        print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
    try:
        edu_choice = int(console_io.prompt("Select education level: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
        display.error("Invalid choice.")
        console_io.pause()
        return
    party = console_io.prompt("Political Party/Affiliation: ")
    manifesto = console_io.prompt("Brief Manifesto/Bio: ")
    address = console_io.prompt("Address: ")
    phone = console_io.prompt("Phone: ")
    email = console_io.prompt("Email: ")
    criminal_record = console_io.prompt("Has Criminal Record? (yes/no): ").lower()
    years_experience = console_io.prompt("Years of Public Service/Political Experience: ")
    data = {
        "full_name": full_name,
        "national_id": national_id,
        "dob_str": dob_str,
        "gender": gender,
        "education_choice": edu_choice,
        "party": party,
        "manifesto": manifesto or "",
        "address": address or "",
        "phone": phone or "",
        "email": email or "",
        "criminal_record": criminal_record,
        "years_experience": years_experience,
    }
    ok, result = candidate_svc.create(auth.current_user["username"], data)
    if not ok:
        if result == "duplicate_national_id":
            display.error("A candidate with this National ID already exists.")
        elif result == "invalid_date":
            display.error("Invalid date format.")
        elif isinstance(result, tuple) and result[0] == "underage":
            display.error(f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {result[1]}")
        elif isinstance(result, tuple) and result[0] == "overage":
            from evoting.core.constants import MAX_CANDIDATE_AGE
            display.error(f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {result[1]}")
        elif result == "criminal_record":
            display.error("Candidates with criminal records are not eligible.")
        else:
            display.error("Invalid input.")
        console_io.pause()
        return
    print()
    display.success(f"Candidate '{full_name}' created successfully! ID: {result}")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_all_candidates(ctx):
    candidate_svc = ctx.candidate_svc
    repo = ctx.repo
    console_io.clear_screen()
    display.header("ALL CANDIDATES", THEME_ADMIN)
    candidates = candidate_svc.get_all()
    if not candidates:
        print()
        display.info("No candidates found.")
        console_io.pause()
        return
    print()
    display.table_header(
        f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}",
        THEME_ADMIN,
    )
    display.table_divider(85, THEME_ADMIN)
    for cid, c in candidates.items():
        status = display.status_badge("Active", True) if c.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
    print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
    console_io.pause()


def update_candidate(ctx):
    repo, auth, candidate_svc = ctx.repo, ctx.auth, ctx.candidate_svc
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header("UPDATE CANDIDATE", THEME_ADMIN)
    if not candidates:
        print()
        display.info("No candidates found.")
        console_io.pause()
        return
    print()
    for cid, c in candidates.items():
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
    try:
        cid = int(console_io.prompt("\nEnter Candidate ID to update: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if cid not in candidates:
        display.error("Candidate not found.")
        console_io.pause()
        return
    c = candidates[cid]
    print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
    display.info("Press Enter to keep current value\n")
    new_name = console_io.prompt(f"Full Name [{c['full_name']}]: ")
    new_party = console_io.prompt(f"Party [{c['party']}]: ")
    new_manifesto = console_io.prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
    new_phone = console_io.prompt(f"Phone [{c['phone']}]: ")
    new_email = console_io.prompt(f"Email [{c['email']}]: ")
    new_address = console_io.prompt(f"Address [{c['address']}]: ")
    new_exp = console_io.prompt(f"Years Experience [{c['years_experience']}]: ")
    updates = {
        "full_name": new_name or None,
        "party": new_party or None,
        "manifesto": new_manifesto or None,
        "phone": new_phone or None,
        "email": new_email or None,
        "address": new_address or None,
        "years_experience": new_exp or None,
    }
    candidate_svc.update(cid, auth.current_user["username"], updates)
    if new_exp:
        try:
            int(new_exp)
        except ValueError:
            display.warning("Invalid number, keeping old value.")
    print()
    display.success(f"Candidate '{c['full_name']}' updated successfully!")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def delete_candidate(ctx):
    repo, auth, candidate_svc, poll_svc = ctx.repo, ctx.auth, ctx.candidate_svc, ctx.poll_svc
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header("DELETE CANDIDATE", THEME_ADMIN)
    if not candidates:
        print()
        display.info("No candidates found.")
        console_io.pause()
        return
    print()
    for cid, c in candidates.items():
        status = display.status_badge("Active", True) if c.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
    try:
        cid = int(console_io.prompt("\nEnter Candidate ID to delete: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if cid not in candidates:
        display.error("Candidate not found.")
        console_io.pause()
        return
    can_ok, can_result = candidate_svc.can_deactivate(cid)
    if not can_ok:
        if can_result == "in_active_poll":
            display.error("Cannot delete - candidate is in active poll.")
        console_io.pause()
        return
    confirm = console_io.prompt(f"Are you sure you want to delete '{candidates[cid]['full_name']}'? (yes/no): ").lower()
    if confirm == "yes":
        candidate_svc.deactivate(cid, auth.current_user["username"])
        print()
        display.success(f"Candidate '{candidates[cid]['full_name']}' has been deactivated.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    else:
        display.info("Deletion cancelled.")
    console_io.pause()


def search_candidates(ctx):
    candidate_svc = ctx.candidate_svc
    console_io.clear_screen()
    display.header("SEARCH CANDIDATES", THEME_ADMIN)
    display.subheader("Search by", THEME_ADMIN_ACCENT)
    display.menu_item(1, "Name", THEME_ADMIN)
    display.menu_item(2, "Party", THEME_ADMIN)
    display.menu_item(3, "Education Level", THEME_ADMIN)
    display.menu_item(4, "Age Range", THEME_ADMIN)
    choice = console_io.prompt("\nChoice: ")
    results = []
    if choice == "1":
        term = console_io.prompt("Enter name to search: ")
        results = candidate_svc.search_by_name(term)
    elif choice == "2":
        term = console_io.prompt("Enter party name: ")
        results = candidate_svc.search_by_party(term)
    elif choice == "3":
        display.subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(console_io.prompt("Select: "))
            edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
            results = candidate_svc.search_by_education(edu)
        except (ValueError, IndexError):
            display.error("Invalid choice.")
            console_io.pause()
            return
    elif choice == "4":
        try:
            min_age = int(console_io.prompt("Min age: "))
            max_age = int(console_io.prompt("Max age: "))
            results = candidate_svc.search_by_age_range(min_age, max_age)
        except ValueError:
            display.error("Invalid input.")
            console_io.pause()
            return
    else:
        display.error("Invalid choice.")
        console_io.pause()
        return
    if not results:
        print()
        display.info("No candidates found matching your criteria.")
    else:
        print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
        display.table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}",
            THEME_ADMIN,
        )
        display.table_divider(75, THEME_ADMIN)
        for c in results:
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
    console_io.pause()


def create_voting_station(ctx):
    repo, auth, station_svc = ctx.repo, ctx.auth, ctx.station_svc
    console_io.clear_screen()
    display.header("CREATE VOTING STATION", THEME_ADMIN)
    print()
    name = console_io.prompt("Station Name: ")
    if not name:
        display.error("Name cannot be empty.")
        console_io.pause()
        return
    location = console_io.prompt("Location/Address: ")
    if not location:
        display.error("Location cannot be empty.")
        console_io.pause()
        return
    region = console_io.prompt("Region/District: ")
    try:
        capacity = int(console_io.prompt("Voter Capacity: "))
        if capacity <= 0:
            display.error("Capacity must be positive.")
            console_io.pause()
            return
    except ValueError:
        display.error("Invalid capacity.")
        console_io.pause()
        return
    supervisor = console_io.prompt("Station Supervisor Name: ")
    contact = console_io.prompt("Contact Phone: ")
    opening_time = console_io.prompt("Opening Time (e.g. 08:00): ")
    closing_time = console_io.prompt("Closing Time (e.g. 17:00): ")
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
    sid = station_svc.create(auth.current_user["username"], data)
    print()
    display.success(f"Voting Station '{name}' created! ID: {sid}")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_all_stations(ctx):
    station_svc, repo = ctx.station_svc, ctx.repo
    console_io.clear_screen()
    display.header("ALL VOTING STATIONS", THEME_ADMIN)
    stations = station_svc.get_all()
    if not stations:
        print()
        display.info("No voting stations found.")
        console_io.pause()
        return
    print()
    display.table_header(
        f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
        THEME_ADMIN,
    )
    display.table_divider(96, THEME_ADMIN)
    for sid, s in stations.items():
        reg_count = station_svc.count_voters_at_station(sid)
        status = display.status_badge("Active", True) if s.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")
    print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
    console_io.pause()


def update_station(ctx):
    repo, auth, station_svc = ctx.repo, ctx.auth, ctx.station_svc
    stations = station_svc.get_all()
    console_io.clear_screen()
    display.header("UPDATE VOTING STATION", THEME_ADMIN)
    if not stations:
        print()
        display.info("No stations found.")
        console_io.pause()
        return
    print()
    for sid, s in stations.items():
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
    try:
        sid = int(console_io.prompt("\nEnter Station ID to update: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if sid not in stations:
        display.error("Station not found.")
        console_io.pause()
        return
    s = stations[sid]
    print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
    display.info("Press Enter to keep current value\n")
    new_name = console_io.prompt(f"Name [{s['name']}]: ")
    new_location = console_io.prompt(f"Location [{s['location']}]: ")
    new_region = console_io.prompt(f"Region [{s['region']}]: ")
    new_capacity = console_io.prompt(f"Capacity [{s['capacity']}]: ")
    new_supervisor = console_io.prompt(f"Supervisor [{s['supervisor']}]: ")
    new_contact = console_io.prompt(f"Contact [{s['contact']}]: ")
    updates = {
        "name": new_name or None,
        "location": new_location or None,
        "region": new_region or None,
        "capacity": new_capacity or None,
        "supervisor": new_supervisor or None,
        "contact": new_contact or None,
    }
    station_svc.update(sid, auth.current_user["username"], updates)
    if new_capacity:
        try:
            int(new_capacity)
        except ValueError:
            display.warning("Invalid number, keeping old value.")
    print()
    display.success(f"Station '{s['name']}' updated successfully!")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def delete_station(ctx):
    repo, auth, station_svc, voter_svc = ctx.repo, ctx.auth, ctx.station_svc, ctx.voter_svc
    stations = station_svc.get_all()
    console_io.clear_screen()
    display.header("DELETE VOTING STATION", THEME_ADMIN)
    if not stations:
        print()
        display.info("No stations found.")
        console_io.pause()
        return
    print()
    for sid, s in stations.items():
        status = display.status_badge("Active", True) if s.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
    try:
        sid = int(console_io.prompt("\nEnter Station ID to delete: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if sid not in stations:
        display.error("Station not found.")
        console_io.pause()
        return
    voter_count = sum(1 for v in repo.voters.values() if v.get("station_id") == sid)
    if voter_count > 0:
        display.warning(f"{voter_count} voters are registered at this station.")
        if console_io.prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
            display.info("Cancelled.")
            console_io.pause()
            return
    if console_io.prompt(f"Confirm deactivation of '{stations[sid]['name']}'? (yes/no): ").lower() == "yes":
        station_svc.deactivate(sid, auth.current_user["username"])
        print()
        display.success(f"Station '{stations[sid]['name']}' deactivated.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    else:
        display.info("Cancelled.")
    console_io.pause()


def create_position(ctx):
    repo, auth, position_svc = ctx.repo, ctx.auth, ctx.position_svc
    console_io.clear_screen()
    display.header("CREATE POSITION", THEME_ADMIN)
    print()
    title = console_io.prompt("Position Title (e.g. President, Governor, Senator): ")
    if not title:
        display.error("Title cannot be empty.")
        console_io.pause()
        return
    description = console_io.prompt("Description: ")
    level = console_io.prompt("Level (National/Regional/Local): ")
    try:
        max_winners = int(console_io.prompt("Number of winners/seats: "))
        if max_winners <= 0:
            display.error("Must be at least 1.")
            console_io.pause()
            return
    except ValueError:
        display.error("Invalid number.")
        console_io.pause()
        return
    min_cand_age = console_io.prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
    min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else MIN_CANDIDATE_AGE
    data = {
        "title": title,
        "description": description or "",
        "level": level,
        "max_winners": max_winners,
        "min_candidate_age": min_cand_age,
    }
    ok, pid = position_svc.create(auth.current_user["username"], data)
    if not ok:
        display.error("Invalid level.")
        console_io.pause()
        return
    print()
    display.success(f"Position '{title}' created! ID: {pid}")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_positions(ctx):
    position_svc = ctx.position_svc
    positions = position_svc.get_all()
    console_io.clear_screen()
    display.header("ALL POSITIONS", THEME_ADMIN)
    if not positions:
        print()
        display.info("No positions found.")
        console_io.pause()
        return
    print()
    display.table_header(
        f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}",
        THEME_ADMIN,
    )
    display.table_divider(70, THEME_ADMIN)
    for pid, p in positions.items():
        status = display.status_badge("Active", True) if p.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")
    print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
    console_io.pause()


def update_position(ctx):
    repo, auth, position_svc = ctx.repo, ctx.auth, ctx.position_svc
    positions = position_svc.get_all()
    console_io.clear_screen()
    display.header("UPDATE POSITION", THEME_ADMIN)
    if not positions:
        print()
        display.info("No positions found.")
        console_io.pause()
        return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try:
        pid = int(console_io.prompt("\nEnter Position ID to update: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in positions:
        display.error("Position not found.")
        console_io.pause()
        return
    p = positions[pid]
    print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
    display.info("Press Enter to keep current value\n")
    new_title = console_io.prompt(f"Title [{p['title']}]: ")
    new_desc = console_io.prompt(f"Description [{p['description'][:50]}]: ")
    new_level = console_io.prompt(f"Level [{p['level']}]: ")
    new_seats = console_io.prompt(f"Seats [{p['max_winners']}]: ")
    updates = {"title": new_title or None, "description": new_desc or None, "level": new_level or None, "max_winners": new_seats or None}
    position_svc.update(pid, auth.current_user["username"], updates)
    if new_seats:
        try:
            int(new_seats)
        except ValueError:
            display.warning("Keeping old value.")
    print()
    display.success("Position updated!")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def delete_position(ctx):
    repo, auth, position_svc = ctx.repo, ctx.auth, ctx.position_svc
    positions = position_svc.get_all()
    console_io.clear_screen()
    display.header("DELETE POSITION", THEME_ADMIN)
    if not positions:
        print()
        display.info("No positions found.")
        console_io.pause()
        return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try:
        pid = int(console_io.prompt("\nEnter Position ID to delete: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in positions:
        display.error("Position not found.")
        console_io.pause()
        return
    for poll in repo.polls.values():
        for pp in poll.get("positions", []):
            if pp["position_id"] == pid and poll["status"] == "open":
                display.error(f"Cannot delete - in active poll: {poll['title']}")
                console_io.pause()
                return
    if console_io.prompt(f"Confirm deactivation of '{positions[pid]['title']}'? (yes/no): ").lower() == "yes":
        position_svc.deactivate(pid, auth.current_user["username"])
        print()
        display.success("Position deactivated.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    console_io.pause()


def create_poll(ctx):
    repo, auth, poll_svc, position_svc, station_svc = ctx.repo, ctx.auth, ctx.poll_svc, ctx.position_svc, ctx.station_svc
    console_io.clear_screen()
    display.header("CREATE POLL / ELECTION", THEME_ADMIN)
    print()
    title = console_io.prompt("Poll/Election Title: ")
    if not title:
        display.error("Title cannot be empty.")
        console_io.pause()
        return
    description = console_io.prompt("Description: ")
    election_type = console_io.prompt("Election Type (General/Primary/By-election/Referendum): ")
    start_date = console_io.prompt("Start Date (YYYY-MM-DD): ")
    end_date = console_io.prompt("End Date (YYYY-MM-DD): ")
    positions = position_svc.get_all()
    if not positions:
        display.error("No positions available. Create positions first.")
        console_io.pause()
        return
    active_positions = {pid: p for pid, p in positions.items() if p.get("is_active", True)}
    if not active_positions:
        display.error("No active positions.")
        console_io.pause()
        return
    display.subheader("Available Positions", THEME_ADMIN_ACCENT)
    for pid, p in active_positions.items():
        print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
    try:
        selected_position_ids = [int(x.strip()) for x in console_io.prompt("\nEnter Position IDs (comma-separated): ").split(",")]
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    position_ids = [spid for spid in selected_position_ids if spid in active_positions]
    if not position_ids:
        display.error("No valid positions selected.")
        console_io.pause()
        return
    stations = station_svc.get_all()
    if not stations:
        display.error("No voting stations. Create stations first.")
        console_io.pause()
        return
    active_stations = {sid: s for sid, s in stations.items() if s.get("is_active", True)}
    display.subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
    for sid, s in active_stations.items():
        print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
    if console_io.prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
        station_ids = list(active_stations.keys())
    else:
        try:
            station_ids = [int(x.strip()) for x in console_io.prompt("Enter Station IDs (comma-separated): ").split(",")]
        except ValueError:
            display.error("Invalid input.")
            console_io.pause()
            return
    data = {
        "title": title,
        "description": description or "",
        "election_type": election_type or "",
        "start_date": start_date,
        "end_date": end_date,
        "position_ids": position_ids,
        "station_ids": station_ids,
    }
    ok, result = poll_svc.create(auth.current_user["username"], data)
    if not ok:
        if result == "end_before_start":
            display.error("End date must be after start date.")
        elif result == "invalid_date":
            display.error("Invalid date format.")
        elif result == "no_valid_positions":
            display.error("No valid positions selected.")
        elif result == "no_stations":
            display.error("No voting stations.")
        else:
            display.error("Invalid input.")
        console_io.pause()
        return
    print()
    display.success(f"Poll '{title}' created! ID: {result}")
    display.warning("Status: DRAFT - Assign candidates and then open the poll.")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_all_polls(ctx):
    repo, poll_svc, candidate_svc = ctx.repo, ctx.poll_svc, ctx.candidate_svc
    polls = poll_svc.get_all()
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header("ALL POLLS / ELECTIONS", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    for pid, poll in polls.items():
        sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
        print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
        print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            cand_names = [candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in candidates]
            cand_display = ", ".join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
            print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
    print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
    console_io.pause()


def update_poll(ctx):
    repo, auth, poll_svc = ctx.repo, ctx.auth, ctx.poll_svc
    polls = poll_svc.get_all()
    console_io.clear_screen()
    display.header("UPDATE POLL", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try:
        pid = int(console_io.prompt("\nEnter Poll ID to update: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in polls:
        display.error("Poll not found.")
        console_io.pause()
        return
    poll = polls[pid]
    if poll["status"] == "open":
        display.error("Cannot update an open poll. Close it first.")
        console_io.pause()
        return
    if poll["status"] == "closed" and poll.get("total_votes_cast", 0) > 0:
        display.error("Cannot update a poll with votes.")
        console_io.pause()
        return
    print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
    display.info("Press Enter to keep current value\n")
    new_title = console_io.prompt(f"Title [{poll['title']}]: ")
    new_desc = console_io.prompt(f"Description [{poll['description'][:50]}]: ")
    new_type = console_io.prompt(f"Election Type [{poll['election_type']}]: ")
    new_start = console_io.prompt(f"Start Date [{poll['start_date']}]: ")
    new_end = console_io.prompt(f"End Date [{poll['end_date']}]: ")
    updates = {
        "title": new_title or None,
        "description": new_desc or None,
        "election_type": new_type or None,
        "start_date": new_start or None,
        "end_date": new_end or None,
    }
    result = poll_svc.update(pid, auth.current_user["username"], updates)
    if result is False:
        pass
    elif result is not True:
        if result == "poll_open":
            display.error("Cannot update an open poll.")
        elif result == "poll_has_votes":
            display.error("Cannot update a poll with votes.")
        console_io.pause()
        return
    print()
    display.success("Poll updated!")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def delete_poll(ctx):
    repo, auth, poll_svc = ctx.repo, ctx.auth, ctx.poll_svc
    polls = poll_svc.get_all()
    console_io.clear_screen()
    display.header("DELETE POLL", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try:
        pid = int(console_io.prompt("\nEnter Poll ID to delete: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in polls:
        display.error("Poll not found.")
        console_io.pause()
        return
    if polls[pid]["status"] == "open":
        display.error("Cannot delete an open poll. Close it first.")
        console_io.pause()
        return
    if polls[pid].get("total_votes_cast", 0) > 0:
        display.warning(f"This poll has {polls[pid]['total_votes_cast']} votes recorded.")
    if console_io.prompt(f"Confirm deletion of '{polls[pid]['title']}'? (yes/no): ").lower() == "yes":
        poll_svc.delete(pid, auth.current_user["username"])
        print()
        display.success(f"Poll '{polls[pid]['title']}' deleted.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    console_io.pause()


def open_close_poll(ctx):
    repo, auth, poll_svc = ctx.repo, ctx.auth, ctx.poll_svc
    polls = poll_svc.get_all()
    console_io.clear_screen()
    display.header("OPEN / CLOSE POLL", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
    try:
        pid = int(console_io.prompt("\nEnter Poll ID: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in polls:
        display.error("Poll not found.")
        console_io.pause()
        return
    poll = polls[pid]
    if poll["status"] == "draft":
        if not any(pos.get("candidate_ids") for pos in poll["positions"]):
            display.error("Cannot open - no candidates assigned.")
            console_io.pause()
            return
        if console_io.prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
            poll_svc.open_poll(pid, auth.current_user["username"])
            print()
            display.success(f"Poll '{poll['title']}' is now OPEN for voting!")
            try:
                repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
    elif poll["status"] == "open":
        if console_io.prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
            poll_svc.close_poll(pid, auth.current_user["username"])
            print()
            display.success(f"Poll '{poll['title']}' is now CLOSED.")
            try:
                repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
    elif poll["status"] == "closed":
        display.info("This poll is already closed.")
        if console_io.prompt("Reopen it? (yes/no): ").lower() == "yes":
            poll_svc.reopen_poll(pid, auth.current_user["username"])
            print()
            display.success("Poll reopened!")
            try:
                repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
    console_io.pause()
