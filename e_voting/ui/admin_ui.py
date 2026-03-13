"""
AdminUI — Admin dashboard and all admin-facing screens.

This is the largest UI module because the admin interface has 31 actions
grouped into six categories:
  1. Candidate Management (CRUD + search)
  2. Voting Station Management (CRUD)
  3. Polls & Positions (CRUD + open/close + candidate assignment)
  4. Voter Management (view, verify, deactivate, search)
  5. Admin Management (create, view, deactivate)
  6. Results & Reports (poll results, statistics, audit log, station breakdown)

Each action is a private method that handles only the UI flow (collecting
input, displaying output) and delegates all business logic to the
appropriate service. This keeps the UI thin and the services testable.

The admin_actions dictionary in show_dashboard() maps menu choices to
handler methods (strategy pattern), avoiding a long if/elif chain.
"""

from e_voting.constants import (
    REQUIRED_EDUCATION_LEVELS, VALID_POSITION_LEVELS,
    MIN_CANDIDATE_AGE, MIN_PASSWORD_LENGTH,
    ADMIN_ROLES, ADMIN_ROLE_DESCRIPTIONS,
    BAR_CHART_WIDTH, TURNOUT_HIGH_THRESHOLD, TURNOUT_MEDIUM_THRESHOLD,
    STATION_LOAD_WARNING_PERCENT, STATION_LOAD_CRITICAL_PERCENT,
)
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, masked_input,
    error, success, warning, info, status_badge, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BRIGHT_WHITE, BRIGHT_YELLOW,
    GREEN, YELLOW, RED, GRAY, DIM, RESET, BOLD, BLACK, BG_GREEN,
)


class AdminUI:
    """Admin dashboard — the central admin control panel.

    All eight service dependencies are injected via the constructor,
    following the Dependency Inversion Principle. The UI never
    instantiates services itself.
    """

    def __init__(self, store, candidate_service, station_service,
                 poll_service, voter_service, admin_service,
                 result_service, auth_service):
        self._store = store
        self._candidates = candidate_service
        self._stations = station_service
        self._polls = poll_service
        self._voters = voter_service
        self._admins = admin_service
        self._results = result_service
        self._auth = auth_service

    def show_dashboard(self):
        """Main admin loop — displays the menu and dispatches actions.
        Uses a dictionary (strategy pattern) instead of long if/elif."""
        admin_actions = {
            "1": self._create_candidate,
            "2": self._view_all_candidates,
            "3": self._update_candidate,
            "4": self._delete_candidate,
            "5": self._search_candidates,
            "6": self._create_station,
            "7": self._view_all_stations,
            "8": self._update_station,
            "9": self._delete_station,
            "10": self._create_position,
            "11": self._view_positions,
            "12": self._update_position,
            "13": self._delete_position,
            "14": self._create_poll,
            "15": self._view_all_polls,
            "16": self._update_poll,
            "17": self._delete_poll,
            "18": self._open_close_poll,
            "19": self._assign_candidates_to_poll,
            "20": self._view_all_voters,
            "21": self._verify_voter,
            "22": self._deactivate_voter,
            "23": self._search_voters,
            "24": self._create_admin,
            "25": self._view_admins,
            "26": self._deactivate_admin,
            "27": self._view_poll_results,
            "28": self._view_detailed_statistics,
            "29": self._view_audit_log,
            "30": self._station_wise_results,
            "31": self._save_data,
        }

        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            user = self._store.current_user
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{user.full_name}{RESET}"
                  f"  {DIM}│  Role: {user.role}{RESET}")

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
            choice = prompt("Enter choice: ")

            if choice in admin_actions:
                admin_actions[choice]()
            elif choice == "32":
                self._store.log_action(
                    "LOGOUT", user.username, "Admin logged out"
                )
                self._store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    # ── Candidate Management ─────────────────────────────────

    def _create_candidate(self):
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty."); pause(); return
        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty."); pause(); return
        if not self._candidates.is_national_id_unique(national_id):
            error("A candidate with this National ID already exists.")
            pause(); return

        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        age, age_err = self._candidates.validate_candidate_age(dob_str)
        if age_err:
            error(age_err); pause(); return

        gender = prompt("Gender (M/F/Other): ").upper()
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice."); pause(); return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input."); pause(); return

        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            error("Candidates with criminal records are not eligible.")
            self._store.log_action(
                "CANDIDATE_REJECTED", self._store.current_user.username,
                f"Candidate {full_name} rejected - criminal record"
            )
            pause(); return

        years_exp_str = prompt(
            "Years of Public Service/Political Experience: "
        )
        try:
            years_experience = int(years_exp_str)
        except ValueError:
            years_experience = 0

        candidate = self._candidates.create(
            full_name, national_id, dob_str, age, gender, education,
            party, manifesto, address, phone, email, years_experience,
            self._store.current_user.username
        )
        print()
        success(f"Candidate '{full_name}' created successfully! "
                f"ID: {candidate.id}")
        pause()

    def _view_all_candidates(self):
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} "
            f"{'Education':<20} {'Status':<10}", THEME_ADMIN
        )
        table_divider(85, THEME_ADMIN)
        for candidate in candidates.values():
            status = (status_badge("Active", True) if candidate.is_active
                      else status_badge("Inactive", False))
            print(f"  {candidate.id:<5} {candidate.full_name:<25} "
                  f"{candidate.party:<20} {candidate.age:<5} "
                  f"{candidate.education:<20} {status}")
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()

    def _update_candidate(self):
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        for candidate in candidates.values():
            print(f"  {THEME_ADMIN}{candidate.id}.{RESET} "
                  f"{candidate.full_name} {DIM}({candidate.party}){RESET}")
        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        candidate = self._candidates.get(cid)
        if not candidate:
            error("Candidate not found."); pause(); return

        print(f"\n  {BOLD}Updating: {candidate.full_name}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_name = prompt(f"Full Name [{candidate.full_name}]: ")
        if new_name:
            updates["full_name"] = new_name
        new_party = prompt(f"Party [{candidate.party}]: ")
        if new_party:
            updates["party"] = new_party
        new_manifesto = prompt(
            f"Manifesto [{candidate.manifesto[:50]}...]: "
        )
        if new_manifesto:
            updates["manifesto"] = new_manifesto
        new_phone = prompt(f"Phone [{candidate.phone}]: ")
        if new_phone:
            updates["phone"] = new_phone
        new_email = prompt(f"Email [{candidate.email}]: ")
        if new_email:
            updates["email"] = new_email
        new_address = prompt(f"Address [{candidate.address}]: ")
        if new_address:
            updates["address"] = new_address
        new_exp = prompt(
            f"Years Experience [{candidate.years_experience}]: "
        )
        if new_exp:
            try:
                updates["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")

        self._candidates.update(
            cid, updates, self._store.current_user.username
        )
        print()
        name = updates.get("full_name", candidate.full_name)
        success(f"Candidate '{name}' updated successfully!")
        pause()

    def _delete_candidate(self):
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        for candidate in candidates.values():
            status = (status_badge("Active", True) if candidate.is_active
                      else status_badge("Inactive", False))
            print(f"  {THEME_ADMIN}{candidate.id}.{RESET} "
                  f"{candidate.full_name} {DIM}({candidate.party}){RESET} "
                  f"{status}")
        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if not self._candidates.get(cid):
            error("Candidate not found."); pause(); return

        can_delete, reason = self._candidates.can_deactivate(cid)
        if not can_delete:
            error(reason); pause(); return

        candidate = self._candidates.get(cid)
        confirm = prompt(
            f"Are you sure you want to delete "
            f"'{candidate.full_name}'? (yes/no): "
        ).lower()
        if confirm == "yes":
            self._candidates.deactivate(
                cid, self._store.current_user.username
            )
            print()
            success(f"Candidate '{candidate.full_name}' has been deactivated.")
        else:
            info("Deletion cancelled.")
        pause()

    def _search_candidates(self):
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Enter name to search: ")
            results = self._candidates.search_by_name(term)
        elif choice == "2":
            term = prompt("Enter party name: ")
            results = self._candidates.search_by_party(term)
        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self._candidates.search_by_education(edu)
            except (ValueError, IndexError):
                error("Invalid choice."); pause(); return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self._candidates.search_by_age_range(
                    min_age, max_age
                )
            except ValueError:
                error("Invalid input."); pause(); return
        else:
            error("Invalid choice."); pause(); return

        if not results:
            print()
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(
                f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} "
                f"{'Education':<20}", THEME_ADMIN
            )
            table_divider(75, THEME_ADMIN)
            for candidate in results:
                print(f"  {candidate.id:<5} {candidate.full_name:<25} "
                      f"{candidate.party:<20} {candidate.age:<5} "
                      f"{candidate.education:<20}")
        pause()

    # ── Station Management ───────────────────────────────────

    def _create_station(self):
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name = prompt("Station Name: ")
        if not name:
            error("Name cannot be empty."); pause(); return
        location = prompt("Location/Address: ")
        if not location:
            error("Location cannot be empty."); pause(); return
        region = prompt("Region/District: ")
        try:
            capacity = int(prompt("Voter Capacity: "))
            if capacity <= 0:
                error("Capacity must be positive."); pause(); return
        except ValueError:
            error("Invalid capacity."); pause(); return
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")

        station = self._stations.create(
            name, location, region, capacity, supervisor, contact,
            opening_time, closing_time,
            self._store.current_user.username
        )
        print()
        success(f"Voting Station '{name}' created! ID: {station.id}")
        pause()

    def _view_all_stations(self):
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self._stations.get_all()
        if not stations:
            print(); info("No voting stations found."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} "
            f"{'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN
        )
        table_divider(96, THEME_ADMIN)
        for sid, station in stations.items():
            reg_count = self._stations.get_registered_voter_count(sid)
            status = (status_badge("Active", True) if station.is_active
                      else status_badge("Inactive", False))
            print(f"  {station.id:<5} {station.name:<25} "
                  f"{station.location:<25} {station.region:<15} "
                  f"{station.capacity:<8} {reg_count:<8} {status}")
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()

    def _update_station(self):
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self._stations.get_all()
        if not stations:
            print(); info("No stations found."); pause(); return
        print()
        for station in stations.values():
            print(f"  {THEME_ADMIN}{station.id}.{RESET} {station.name} "
                  f"{DIM}- {station.location}{RESET}")
        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        station = self._stations.get(sid)
        if not station:
            error("Station not found."); pause(); return

        print(f"\n  {BOLD}Updating: {station.name}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_name = prompt(f"Name [{station.name}]: ")
        if new_name:
            updates["name"] = new_name
        new_location = prompt(f"Location [{station.location}]: ")
        if new_location:
            updates["location"] = new_location
        new_region = prompt(f"Region [{station.region}]: ")
        if new_region:
            updates["region"] = new_region
        new_capacity = prompt(f"Capacity [{station.capacity}]: ")
        if new_capacity:
            try:
                updates["capacity"] = int(new_capacity)
            except ValueError:
                warning("Invalid number, keeping old value.")
        new_supervisor = prompt(f"Supervisor [{station.supervisor}]: ")
        if new_supervisor:
            updates["supervisor"] = new_supervisor
        new_contact = prompt(f"Contact [{station.contact}]: ")
        if new_contact:
            updates["contact"] = new_contact

        self._stations.update(
            sid, updates, self._store.current_user.username
        )
        name = updates.get("name", station.name)
        print()
        success(f"Station '{name}' updated successfully!")
        pause()

    def _delete_station(self):
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        stations = self._stations.get_all()
        if not stations:
            print(); info("No stations found."); pause(); return
        print()
        for station in stations.values():
            status = (status_badge("Active", True) if station.is_active
                      else status_badge("Inactive", False))
            print(f"  {THEME_ADMIN}{station.id}.{RESET} {station.name} "
                  f"{DIM}({station.location}){RESET} {status}")
        try:
            sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        station = self._stations.get(sid)
        if not station:
            error("Station not found."); pause(); return

        voter_count = self._stations.get_registered_voter_count(sid)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                info("Cancelled."); pause(); return

        if prompt(f"Confirm deactivation of '{station.name}'? "
                  "(yes/no): ").lower() == "yes":
            self._stations.deactivate(
                sid, self._store.current_user.username
            )
            print()
            success(f"Station '{station.name}' deactivated.")
        else:
            info("Cancelled.")
        pause()

    # ── Position Management ──────────────────────────────────

    def _create_position(self):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt(
            "Position Title (e.g. President, Governor, Senator): "
        )
        if not title:
            error("Title cannot be empty."); pause(); return
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in VALID_POSITION_LEVELS:
            error("Invalid level."); pause(); return
        try:
            max_winners = int(prompt("Number of winners/seats: "))
            if max_winners <= 0:
                error("Must be at least 1."); pause(); return
        except ValueError:
            error("Invalid number."); pause(); return
        min_age_str = prompt(
            f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: "
        )
        min_age = (int(min_age_str) if min_age_str.isdigit()
                   else MIN_CANDIDATE_AGE)

        position = self._polls.create_position(
            title, description, level, max_winners, min_age,
            self._store.current_user.username
        )
        print()
        success(f"Position '{title}' created! ID: {position.id}")
        pause()

    def _view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} "
            f"{'Min Age':<10} {'Status':<10}", THEME_ADMIN
        )
        table_divider(70, THEME_ADMIN)
        for position in positions.values():
            status = (status_badge("Active", True) if position.is_active
                      else status_badge("Inactive", False))
            print(f"  {position.id:<5} {position.title:<25} "
                  f"{position.level:<12} {position.max_winners:<8} "
                  f"{position.min_candidate_age:<10} {status}")
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
        pause()

    def _update_position(self):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        for position in positions.values():
            print(f"  {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        position = self._store.positions.get(pid)
        if not position:
            error("Position not found."); pause(); return

        print(f"\n  {BOLD}Updating: {position.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_title = prompt(f"Title [{position.title}]: ")
        if new_title:
            updates["title"] = new_title
        new_desc = prompt(f"Description [{position.description[:50]}]: ")
        if new_desc:
            updates["description"] = new_desc
        new_level = prompt(f"Level [{position.level}]: ")
        if new_level and new_level.lower() in VALID_POSITION_LEVELS:
            updates["level"] = new_level.capitalize()
        new_seats = prompt(f"Seats [{position.max_winners}]: ")
        if new_seats:
            try:
                updates["max_winners"] = int(new_seats)
            except ValueError:
                warning("Keeping old value.")

        self._polls.update_position(
            pid, updates, self._store.current_user.username
        )
        print()
        success("Position updated!")
        pause()

    def _delete_position(self):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        for position in positions.values():
            print(f"  {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if pid not in positions:
            error("Position not found."); pause(); return

        can_delete, reason = self._polls.can_deactivate_position(pid)
        if not can_delete:
            error(reason); pause(); return

        position = positions[pid]
        if prompt(f"Confirm deactivation of '{position.title}'? "
                  "(yes/no): ").lower() == "yes":
            self._polls.deactivate_position(
                pid, self._store.current_user.username
            )
            print()
            success("Position deactivated.")
        pause()

    # ── Poll Management ──────────────────────────────────────

    def _create_poll(self):
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty."); pause(); return
        description = prompt("Description: ")
        election_type = prompt(
            "Election Type (General/Primary/By-election/Referendum): "
        )
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")

        _, _, date_err = self._polls.validate_poll_dates(start_date, end_date)
        if date_err:
            error(date_err); pause(); return

        active_positions = self._polls.get_active_positions()
        if not active_positions:
            error("No active positions. Create positions first.")
            pause(); return

        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for position in active_positions.values():
            print(f"    {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}) - "
                  f"{position.max_winners} seat(s){RESET}")
        try:
            selected_ids = [
                int(x.strip()) for x in
                prompt("\nEnter Position IDs (comma-separated): ").split(",")
            ]
        except ValueError:
            error("Invalid input."); pause(); return

        active_stations = self._stations.get_active()
        if not active_stations:
            error("No voting stations. Create stations first.")
            pause(); return

        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for station in active_stations.values():
            print(f"    {THEME_ADMIN}{station.id}.{RESET} {station.name} "
                  f"{DIM}({station.location}){RESET}")
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            station_ids = list(active_stations.keys())
        else:
            try:
                station_ids = [
                    int(x.strip()) for x in
                    prompt("Enter Station IDs (comma-separated): ").split(",")
                ]
            except ValueError:
                error("Invalid input."); pause(); return

        poll, poll_err = self._polls.create_poll(
            title, description, election_type, start_date, end_date,
            selected_ids, station_ids,
            self._store.current_user.username
        )
        if poll_err:
            error(poll_err); pause(); return

        print()
        success(f"Poll '{title}' created! ID: {poll.id}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
        pause()

    def _view_all_polls(self):
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        for poll in polls.values():
            status_color = self._poll_status_color(poll.status)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll.id}: "
                  f"{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  "
                  f"{DIM}│  Status:{RESET} {status_color}{BOLD}"
                  f"{poll.status.upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll.start_date} to "
                  f"{poll.end_date}  {DIM}│  Votes:{RESET} "
                  f"{poll.total_votes_cast}")
            for pos in poll.positions:
                cand_names = [
                    self._store.candidates[cid].full_name
                    for cid in pos.candidate_ids
                    if cid in self._store.candidates
                ]
                cand_display = (', '.join(cand_names) if cand_names
                                else f"{DIM}None assigned{RESET}")
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} "
                      f"{pos.position_title}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        pause()

    def _update_poll(self):
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot update an open poll. Close it first.")
            pause(); return
        if poll.is_closed() and poll.total_votes_cast > 0:
            error("Cannot update a poll with votes."); pause(); return

        print(f"\n  {BOLD}Updating: {poll.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_title = prompt(f"Title [{poll.title}]: ")
        if new_title:
            updates["title"] = new_title
        new_desc = prompt(f"Description [{poll.description[:50]}]: ")
        if new_desc:
            updates["description"] = new_desc
        new_type = prompt(f"Election Type [{poll.election_type}]: ")
        if new_type:
            updates["election_type"] = new_type
        new_start = prompt(f"Start Date [{poll.start_date}]: ")
        if new_start:
            _, _, err = self._polls.validate_poll_dates(
                new_start, poll.end_date
            )
            if not err:
                updates["start_date"] = new_start
            else:
                warning("Invalid date, keeping old value.")
        new_end = prompt(f"End Date [{poll.end_date}]: ")
        if new_end:
            start = updates.get("start_date", poll.start_date)
            _, _, err = self._polls.validate_poll_dates(start, new_end)
            if not err:
                updates["end_date"] = new_end
            else:
                warning("Invalid date, keeping old value.")

        self._polls.update_poll(
            pid, updates, self._store.current_user.username
        )
        print()
        success("Poll updated!")
        pause()

    def _delete_poll(self):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot delete an open poll. Close it first.")
            pause(); return
        if poll.total_votes_cast > 0:
            warning(f"This poll has {poll.total_votes_cast} votes recorded.")
        if prompt(f"Confirm deletion of '{poll.title}'? "
                  "(yes/no): ").lower() == "yes":
            self._polls.delete_poll(
                pid, self._store.current_user.username
            )
            print()
            success(f"Poll '{poll.title}' deleted.")
        pause()

    def _open_close_poll(self):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = self._poll_status_color(poll.status)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title}  "
                  f"{sc}{BOLD}{poll.status.upper()}{RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return

        username = self._store.current_user.username
        if poll.is_draft():
            if not poll.has_any_candidates():
                error("Cannot open - no candidates assigned.")
                pause(); return
            if prompt(f"Open poll '{poll.title}'? Voting will begin. "
                      "(yes/no): ").lower() == "yes":
                self._polls.open_poll(pid, username)
                print()
                success(f"Poll '{poll.title}' is now OPEN for voting!")
        elif poll.is_open():
            if prompt(f"Close poll '{poll.title}'? No more votes accepted. "
                      "(yes/no): ").lower() == "yes":
                self._polls.close_poll(pid, username)
                print()
                success(f"Poll '{poll.title}' is now CLOSED.")
        elif poll.is_closed():
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                self._polls.reopen_poll(pid, username)
                print()
                success("Poll reopened!")
        pause()

    def _assign_candidates_to_poll(self):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        if not self._candidates.get_all():
            print(); info("No candidates found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot modify candidates of an open poll.")
            pause(); return

        for idx, pos in enumerate(poll.positions):
            subheader(f"Position: {pos.position_title}",
                      THEME_ADMIN_ACCENT)
            current_cands = [
                f"{cid}: {self._store.candidates[cid].full_name}"
                for cid in pos.candidate_ids
                if cid in self._store.candidates
            ]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                info("No candidates assigned yet.")

            eligible = self._polls.get_eligible_candidates(pos.position_id)
            if not eligible:
                info("No eligible candidates found.")
                continue

            subheader("Available Candidates", THEME_ADMIN)
            for candidate in eligible.values():
                marker = (f" {GREEN}[ASSIGNED]{RESET}"
                          if candidate.id in pos.candidate_ids else "")
                print(f"    {THEME_ADMIN}{candidate.id}.{RESET} "
                      f"{candidate.full_name} {DIM}({candidate.party}) "
                      f"- Age: {candidate.age}, "
                      f"Edu: {candidate.education}{RESET}{marker}")

            if prompt(f"\nModify candidates for {pos.position_title}? "
                      "(yes/no): ").lower() == "yes":
                try:
                    new_ids = [
                        int(x.strip()) for x in
                        prompt("Enter Candidate IDs "
                               "(comma-separated): ").split(",")
                    ]
                    count = self._polls.assign_candidates_to_position(
                        pid, idx, new_ids,
                        self._store.current_user.username
                    )
                    success(f"{count} candidate(s) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        pause()

    # ── Voter Management ─────────────────────────────────────

    def _view_all_voters(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self._voters.get_all()
        if not voters:
            print(); info("No voters registered."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} "
            f"{'Verified':<10} {'Active':<8}", THEME_ADMIN
        )
        table_divider(70, THEME_ADMIN)
        for voter in voters.values():
            verified = (status_badge("Yes", True) if voter.is_verified
                        else status_badge("No", False))
            active = (status_badge("Yes", True) if voter.is_active
                      else status_badge("No", False))
            print(f"  {voter.id:<5} {voter.full_name:<25} "
                  f"{voter.voter_card_number:<15} {voter.station_id:<6} "
                  f"{verified:<19} {active}")
        verified_count = self._voters.get_verified_count()
        unverified_count = self._voters.get_unverified_count()
        print(f"\n  {DIM}Total: {len(voters)}  │  "
              f"Verified: {verified_count}  │  "
              f"Unverified: {unverified_count}{RESET}")
        pause()

    def _verify_voter(self):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        unverified = self._voters.get_unverified()
        if not unverified:
            print(); info("No unverified voters."); pause(); return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for voter in unverified.values():
            print(f"  {THEME_ADMIN}{voter.id}.{RESET} {voter.full_name} "
                  f"{DIM}│ NID: {voter.national_id} "
                  f"│ Card: {voter.voter_card_number}{RESET}")
        print()
        menu_item(1, "Verify a single voter", THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        username = self._store.current_user.username
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input."); pause(); return
            ok, err = self._voters.verify(vid, username)
            if not ok:
                (error if err != "Already verified." else info)(err)
            else:
                voter = self._voters.get(vid)
                print()
                success(f"Voter '{voter.full_name}' verified!")
        elif choice == "2":
            count = self._voters.verify_all_unverified(username)
            print()
            success(f"{count} voters verified!")
        pause()

    def _deactivate_voter(self):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self._voters.get_all():
            print(); info("No voters found."); pause(); return
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input."); pause(); return

        voter = self._voters.get(vid)
        if not voter:
            error("Voter not found."); pause(); return
        if not voter.is_active:
            info("Already deactivated."); pause(); return

        if prompt(f"Deactivate '{voter.full_name}'? "
                  "(yes/no): ").lower() == "yes":
            self._voters.deactivate(
                vid, self._store.current_user.username
            )
            print()
            success("Voter deactivated.")
        pause()

    def _search_voters(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID", THEME_ADMIN)
        menu_item(4, "Station", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Name: ")
            results = self._voters.search_by_name(term)
        elif choice == "2":
            term = prompt("Card Number: ")
            results = self._voters.search_by_card(term)
        elif choice == "3":
            term = prompt("National ID: ")
            results = self._voters.search_by_national_id(term)
        elif choice == "4":
            try:
                sid = int(prompt("Station ID: "))
                results = self._voters.search_by_station(sid)
            except ValueError:
                error("Invalid input."); pause(); return
        else:
            error("Invalid choice."); pause(); return

        if not results:
            print()
            info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for voter in results:
                verified = (status_badge("Verified", True)
                            if voter.is_verified
                            else status_badge("Unverified", False))
                print(f"  {THEME_ADMIN}ID:{RESET} {voter.id}  "
                      f"{DIM}│{RESET}  {voter.full_name}  "
                      f"{DIM}│  Card:{RESET} {voter.voter_card_number}"
                      f"  {DIM}│{RESET}  {verified}")
        pause()

    # ── Admin Management ─────────────────────────────────────

    def _create_admin(self):
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if not self._store.current_user.is_super_admin():
            print()
            error("Only super admins can create admin accounts.")
            pause(); return
        print()
        username = prompt("Username: ")
        if not username:
            error("Username cannot be empty."); pause(); return
        if not self._admins.is_username_unique(username):
            error("Username already exists."); pause(); return
        full_name = prompt("Full Name: ")
        email = prompt("Email: ")
        password = masked_input("Password: ").strip()
        if len(password) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least "
                  f"{MIN_PASSWORD_LENGTH} characters.")
            pause(); return

        subheader("Available Roles", THEME_ADMIN_ACCENT)
        menu_item(1, f"super_admin {DIM}─ Full access{RESET}",
                  THEME_ADMIN)
        menu_item(2, f"election_officer {DIM}─ Manage polls and "
                     f"candidates{RESET}", THEME_ADMIN)
        menu_item(3, f"station_manager {DIM}─ Manage stations and "
                     f"verify voters{RESET}", THEME_ADMIN)
        menu_item(4, f"auditor {DIM}─ Read-only access{RESET}",
                  THEME_ADMIN)
        role_choice = prompt("\nSelect role (1-4): ")
        if role_choice not in ADMIN_ROLES:
            error("Invalid role."); pause(); return
        role = ADMIN_ROLES[role_choice]

        admin = self._admins.create(
            username, full_name, email,
            self._auth.hash_password(password), role,
            self._store.current_user.username
        )
        print()
        success(f"Admin '{username}' created with role: {role}")
        pause()

    def _view_admins(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        admins = self._admins.get_all()
        table_header(
            f"{'ID':<5} {'Username':<20} {'Full Name':<25} "
            f"{'Role':<20} {'Active':<8}", THEME_ADMIN
        )
        table_divider(78, THEME_ADMIN)
        for admin in admins.values():
            active = (status_badge("Yes", True) if admin.is_active
                      else status_badge("No", False))
            print(f"  {admin.id:<5} {admin.username:<20} "
                  f"{admin.full_name:<25} {admin.role:<20} {active}")
        print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
        pause()

    def _deactivate_admin(self):
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        if not self._store.current_user.is_super_admin():
            print()
            error("Only super admins can deactivate admins.")
            pause(); return
        print()
        admins = self._admins.get_all()
        for admin in admins.values():
            active = (status_badge("Active", True) if admin.is_active
                      else status_badge("Inactive", False))
            print(f"  {THEME_ADMIN}{admin.id}.{RESET} {admin.username} "
                  f"{DIM}({admin.role}){RESET} {active}")
        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if aid not in admins:
            error("Admin not found."); pause(); return
        if aid == self._store.current_user.id:
            error("Cannot deactivate your own account.")
            pause(); return

        admin = admins[aid]
        if prompt(f"Deactivate '{admin.username}'? "
                  "(yes/no): ").lower() == "yes":
            self._admins.deactivate(
                aid, self._store.current_user.username
            )
            print()
            success("Admin deactivated.")
        pause()

    # ── Results & Reports ────────────────────────────────────

    def _view_poll_results(self):
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        print()
        header(f"RESULTS: {poll.title}", THEME_ADMIN)
        sc = GREEN if poll.is_open() else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll.status.upper()}"
              f"{RESET}  {DIM}│  Votes:{RESET} {BOLD}"
              f"{poll.total_votes_cast}{RESET}")

        turnout, eligible = self._results.calculate_turnout(poll)
        tc = (GREEN if turnout > TURNOUT_HIGH_THRESHOLD
              else (YELLOW if turnout > TURNOUT_MEDIUM_THRESHOLD else RED))
        print(f"  {DIM}Eligible:{RESET} {eligible}  "
              f"{DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")

        for pos in poll.positions:
            subheader(f"{pos.position_title} "
                      f"(Seats: {pos.max_winners})", THEME_ADMIN_ACCENT)
            vote_counts, abstain_count, total_pos = (
                self._results.get_position_tally(pid, pos.position_id)
            )
            sorted_counts = sorted(
                vote_counts.items(), key=lambda x: x[1], reverse=True
            )
            for rank, (cid, count) in enumerate(sorted_counts, 1):
                cand = self._store.candidates.get(cid)
                pct = (count / total_pos * 100) if total_pos > 0 else 0
                bar_len = int(pct / 2)
                bar = (f"{THEME_ADMIN}{'█' * bar_len}"
                       f"{GRAY}{'░' * (BAR_CHART_WIDTH - bar_len)}{RESET}")
                winner = (f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}"
                          if rank <= pos.max_winners else "")
                name = cand.full_name if cand else "?"
                party = cand.party if cand else "?"
                print(f"    {BOLD}{rank}. {name}{RESET} "
                      f"{DIM}({party}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} "
                      f"({pct:.1f}%){winner}")
            if abstain_count > 0:
                pct = ((abstain_count / total_pos * 100)
                       if total_pos > 0 else 0)
                print(f"    {GRAY}Abstained: {abstain_count} "
                      f"({pct:.1f}%){RESET}")
            if not vote_counts:
                info("    No votes recorded for this position.")
        pause()

    def _view_detailed_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)

        stats = self._results.get_system_statistics()
        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        print(f"  {THEME_ADMIN}Candidates:{RESET}  "
              f"{stats['total_candidates']} "
              f"{DIM}(Active: {stats['active_candidates']}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      "
              f"{stats['total_voters']} "
              f"{DIM}(Verified: {stats['verified_voters']}, "
              f"Active: {stats['active_voters']}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    "
              f"{stats['total_stations']} "
              f"{DIM}(Active: {stats['active_stations']}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       "
              f"{stats['total_polls']} "
              f"{DIM}({GREEN}Open: {stats['open_polls']}{RESET}{DIM}, "
              f"{RED}Closed: {stats['closed_polls']}{RESET}{DIM}, "
              f"{YELLOW}Draft: {stats['draft_polls']}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} "
              f"{stats['total_votes']}")

        gender_counts, age_groups, total_voters = (
            self._results.get_voter_demographics()
        )
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        for gender, count in gender_counts.items():
            pct = (count / total_voters * 100) if total_voters > 0 else 0
            print(f"    {gender}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in age_groups.items():
            pct = (count / total_voters * 100) if total_voters > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) "
                  f"{THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")

        station_load = self._results.get_station_load()
        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for entry in station_load:
            station = entry["station"]
            lp = entry["load_percent"]
            vc = entry["voter_count"]
            lc = (RED if lp > STATION_LOAD_CRITICAL_PERCENT
                  else (YELLOW if lp > STATION_LOAD_WARNING_PERCENT
                        else GREEN))
            st = (f"{RED}{BOLD}OVERLOADED{RESET}" if entry["is_overloaded"]
                  else f"{GREEN}OK{RESET}")
            print(f"    {station.name}: {vc}/{station.capacity} "
                  f"{lc}({lp:.0f}%){RESET} {st}")

        party_dist = self._results.get_party_distribution()
        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        for party, count in party_dist.items():
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")

        edu_dist = self._results.get_education_distribution()
        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        for edu, count in edu_dist.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def _view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        audit_log = self._store.audit_log
        if not audit_log:
            print(); info("No audit records."); pause(); return
        print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1, "Last 20 entries", THEME_ADMIN)
        menu_item(2, "All entries", THEME_ADMIN)
        menu_item(3, "Filter by action type", THEME_ADMIN)
        menu_item(4, "Filter by user", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        entries = audit_log
        if choice == "1":
            entries = self._results.get_audit_log(
                filter_type="last", limit=20
            )
        elif choice == "3":
            action_types = self._results.get_unique_action_types()
            for i, action_type in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {action_type}")
            try:
                at_choice = int(prompt("Select action type: "))
                entries = self._results.get_audit_log(
                    filter_type="action",
                    filter_value=action_types[at_choice - 1]
                )
            except (ValueError, IndexError):
                error("Invalid choice."); pause(); return
        elif choice == "4":
            user_filter = prompt("Enter username/card number: ")
            entries = self._results.get_audit_log(
                filter_type="user", filter_value=user_filter
            )

        print()
        table_header(
            f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}",
            THEME_ADMIN
        )
        table_divider(100, THEME_ADMIN)
        for entry in entries:
            action = entry["action"]
            if "CREATE" in action or action == "LOGIN":
                ac = GREEN
            elif "DELETE" in action or "DEACTIVATE" in action:
                ac = RED
            elif "UPDATE" in action:
                ac = YELLOW
            else:
                ac = RESET
            print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  "
                  f"{ac}{action:<25}{RESET} {entry['user']:<20} "
                  f"{DIM}{entry['details'][:50]}{RESET}")
        pause()

    def _station_wise_results(self):
        clear_screen()
        header("STATION-WISE RESULTS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return

        print()
        header(f"STATION RESULTS: {poll.title}", THEME_ADMIN)
        station_data = self._results.get_station_results(pid)
        if not station_data:
            info("No station data available."); pause(); return

        for entry in station_data:
            station = entry["station"]
            subheader(f"{station.name}  ({station.location})",
                      BRIGHT_WHITE)
            tc = (GREEN if entry["turnout"] > TURNOUT_HIGH_THRESHOLD
                  else (YELLOW if entry["turnout"] > TURNOUT_MEDIUM_THRESHOLD
                        else RED))
            print(f"  {DIM}Registered:{RESET} {entry['registered']}  "
                  f"{DIM}│  Voted:{RESET} {entry['unique_voters']}  "
                  f"{DIM}│  Turnout:{RESET} {tc}{BOLD}"
                  f"{entry['turnout']:.1f}%{RESET}")

            for pos_result in entry["position_results"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ "
                      f"{pos_result['position_title']}:{RESET}")
                total = pos_result["total"]
                sorted_counts = sorted(
                    pos_result["vote_counts"].items(),
                    key=lambda x: x[1], reverse=True
                )
                for cid, count in sorted_counts:
                    cand = self._store.candidates.get(cid)
                    pct = (count / total * 100) if total > 0 else 0
                    name = cand.full_name if cand else "?"
                    party = cand.party if cand else "?"
                    print(f"      {name} {DIM}({party}){RESET}: "
                          f"{BOLD}{count}{RESET} ({pct:.1f}%)")
                if pos_result["abstain_count"] > 0:
                    ac = pos_result["abstain_count"]
                    pct = (ac / total * 100) if total > 0 else 0
                    print(f"      {GRAY}Abstained: {ac} "
                          f"({pct:.1f}%){RESET}")
        pause()

    # ── System ───────────────────────────────────────────────

    def _save_data(self):
        self._store.save()
        info("Data saved successfully")
        pause()

    # ── Helpers ──────────────────────────────────────────────

    def _display_poll_list(self, polls):
        for poll in polls.values():
            sc = self._poll_status_color(poll.status)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{sc}({poll.status}){RESET}")

    @staticmethod
    def _poll_status_color(status):
        if status == "open":
            return GREEN
        if status == "draft":
            return YELLOW
        return RED
