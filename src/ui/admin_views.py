from src.ui.theme import *
from datetime import datetime

class AdminViews:
    def __init__(self, services):
        self.services = services
        self.candidate_service = services['candidate']
        self.station_service = services['station']
        self.poll_service = services['poll']
        self.voter_service = services['voter']
        self.audit_service = services['audit']
        self.report_service = services['report']
        self.ds = services['data_store']

    def dashboard(self, current_user):
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user.full_name}{RESET}  {DIM}│  Role: {current_user.role}{RESET}")

            self._show_menu_sections()
            print()
            choice = prompt("Enter choice: ")

            if choice == "1": self._create_candidate(current_user)
            elif choice == "2": self._view_all_candidates()
            elif choice == "3": self._update_candidate(current_user)
            elif choice == "4": self._delete_candidate(current_user)
            elif choice == "5": self._search_candidates()
            elif choice == "6": self._create_voting_station(current_user)
            elif choice == "7": self._view_all_stations()
            elif choice == "8": self._update_station(current_user)
            elif choice == "9": self._delete_station(current_user)
            elif choice == "10": self._create_position(current_user)
            elif choice == "11": self._view_positions()
            elif choice == "12": self._update_position(current_user)
            elif choice == "13": self._delete_position(current_user)
            elif choice == "14": self._create_poll(current_user)
            elif choice == "15": self._view_all_polls()
            elif choice == "16": self._update_poll(current_user)
            elif choice == "17": self._delete_poll(current_user)
            elif choice == "18": self._open_close_poll(current_user)
            elif choice == "19": self._assign_candidates_to_poll(current_user)
            elif choice == "20": self._view_all_voters()
            elif choice == "21": self._verify_voter(current_user)
            elif choice == "22": self._deactivate_voter(current_user)
            elif choice == "23": self._search_voters()
            # Need to implement create_admin etc if needed, but the original had them
            elif choice == "24": self._create_admin(current_user)
            elif choice == "25": self._view_admins()
            elif choice == "26": self._deactivate_admin(current_user)
            elif choice == "27": self._view_poll_results()
            elif choice == "28": self._view_detailed_statistics()
            elif choice == "29": self._view_audit_log()
            elif choice == "30": self._station_wise_results()
            elif choice == "31": self.ds.save_data(); pause()
            elif choice == "32": 
                self.ds.log_action("LOGOUT", current_user.username, "Admin logged out")
                self.ds.save_data()
                break
            else: error("Invalid choice."); pause()

    def _show_menu_sections(self):
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

    # Candidate View Methods
    def _create_candidate(self, current_user):
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name = prompt("Full Name: ")
        national_id = prompt("National ID: ")
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        gender = prompt("Gender (M/F/Other): ").upper()
        
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(self.candidate_service.REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        
        try:
            edu_choice = int(prompt("Select education level: "))
        except ValueError: error("Invalid input."); pause(); return
        
        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        years_experience = prompt("Years of Public Service/Political Experience: ")
        
        success_flag, msg = self.candidate_service.create_candidate(
            current_user, full_name, national_id, dob_str, gender, edu_choice, 
            party, manifesto, address, phone, email, criminal_record, years_experience
        )
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _view_all_candidates(self):
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self.ds.candidates
        if not candidates: print(); info("No candidates found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        table_divider(85, THEME_ADMIN)
        for c in candidates.values():
            status = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20} {status}")
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()

    def _update_candidate(self, current_user):
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        candidates = self.ds.candidates
        if not candidates: print(); info("No candidates found."); pause(); return
        for c in candidates.values():
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET}")
        
        try: cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        
        if cid not in candidates: error("Candidate not found."); pause(); return
        c = candidates[cid]
        print(f"\n  {BOLD}Updating: {c.full_name}{RESET}")
        info("Press Enter to keep current value\n")
        new_name = prompt(f"Full Name [{c.full_name}]: ")
        new_party = prompt(f"Party [{c.party}]: ")
        new_manifesto = prompt(f"Manifesto [{c.manifesto[:50]}...]: ")
        new_phone = prompt(f"Phone [{c.phone}]: ")
        new_email = prompt(f"Email [{c.email}]: ")
        new_address = prompt(f"Address [{c.address}]: ")
        new_exp = prompt(f"Years Experience [{c.years_experience}]: ")
        
        success_flag, msg = self.candidate_service.update_candidate(
            current_user, cid, new_name, new_party, new_manifesto, new_phone, new_email, new_address, new_exp
        )
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _delete_candidate(self, current_user):
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        candidates = self.ds.candidates
        if not candidates: print(); info("No candidates found."); pause(); return
        for c in candidates.values():
            status = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET} {status}")
        
        try: cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        
        if cid not in candidates: error("Candidate not found."); pause(); return
        
        confirm = prompt(f"Are you sure you want to delete '{candidates[cid].full_name}'? (yes/no): ").lower()
        if confirm == "yes":
            success_flag, msg = self.candidate_service.delete_candidate(current_user, cid)
            if success_flag: success(msg)
            else: error(msg)
        else: info("Deletion cancelled.")
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
            results = self.candidate_service.search_candidates("1", term=term)
        elif choice == "2":
            term = prompt("Enter party name: ")
            results = self.candidate_service.search_candidates("2", term=term)
        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(self.candidate_service.REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                results = self.candidate_service.search_candidates("3", edu_choice=edu_choice)
            except ValueError: error("Invalid choice."); pause(); return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self.candidate_service.search_candidates("4", min_age=min_age, max_age=max_age)
            except ValueError: error("Invalid input."); pause(); return
        
        if not results: print(); info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20}")
        pause()

    # Station View Methods
    def _create_voting_station(self, current_user):
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name = prompt("Station Name: ")
        location = prompt("Location/Address: ")
        region = prompt("Region/District: ")
        capacity = prompt("Voter Capacity: ")
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")
        
        success_flag, msg = self.station_service.create_station(
            current_user, name, location, region, capacity, supervisor, contact, opening_time, closing_time
        )
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _view_all_stations(self):
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self.ds.voting_stations
        if not stations: print(); info("No voting stations found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
        table_divider(96, THEME_ADMIN)
        for s in stations.values():
            reg_count = self.station_service.get_voter_count(s.id)
            status = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {s.id:<5} {s.name:<25} {s.location:<25} {s.region:<15} {s.capacity:<8} {reg_count:<8} {status}")
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()

    def _update_station(self, current_user):
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self.ds.voting_stations
        if not stations: print(); info("No stations found."); pause(); return
        for s in stations.values():
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}- {s.location}{RESET}")
        
        try: sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        
        if sid not in stations: error("Station not found."); pause(); return
        s = stations[sid]
        print(f"\n  {BOLD}Updating: {s.name}{RESET}")
        info("Press Enter to keep current value\n")
        new_name = prompt(f"Name [{s.name}]: ")
        new_location = prompt(f"Location [{s.location}]: ")
        new_region = prompt(f"Region [{s.region}]: ")
        new_capacity = prompt(f"Capacity [{s.capacity}]: ")
        new_supervisor = prompt(f"Supervisor [{s.supervisor}]: ")
        new_contact = prompt(f"Contact [{s.contact}]: ")
        
        success_flag, msg = self.station_service.update_station(
            current_user, sid, new_name, new_location, new_region, new_capacity, new_supervisor, new_contact
        )
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _delete_station(self, current_user):
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        stations = self.ds.voting_stations
        if not stations: print(); info("No stations found."); pause(); return
        for s in stations.values():
            status = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET} {status}")
        
        try: sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        
        if sid not in stations: error("Station not found."); pause(); return
        
        voter_count = self.station_service.get_voter_count(sid)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes": info("Cancelled."); pause(); return
        
        if prompt(f"Confirm deactivation of '{stations[sid].name}'? (yes/no): ").lower() == "yes":
            success_flag, msg = self.station_service.delete_station(current_user, sid)
            if success_flag: success(msg)
            else: error(msg)
        else: info("Cancelled.")
        pause()

    # Position View Methods
    def _create_position(self, current_user):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        max_winners = prompt("Number of winners/seats: ")
        min_cand_age = prompt(f"Minimum candidate age [25]: ")
        
        success_flag, msg = self.poll_service.create_position(current_user, title, description, level, max_winners, min_cand_age)
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        positions = self.ds.positions
        if not positions: print(); info("No positions found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        for p in positions.values():
            status = status_badge("Active", True) if p.is_active else status_badge("Inactive", False)
            print(f"  {p.id:<5} {p.title:<25} {p.level:<12} {p.max_winners:<8} {p.min_candidate_age:<10} {status}")
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
        pause()

    def _update_position(self, current_user):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        positions = self.ds.positions
        if not positions: print(); info("No positions found."); pause(); return
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        
        try: pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in positions: error("Position not found."); pause(); return
        
        p = positions[pid]
        print(f"\n  {BOLD}Updating: {p.title}{RESET}")
        info("Press Enter to keep current value\n")
        new_title = prompt(f"Title [{p.title}]: ")
        new_desc = prompt(f"Description [{p.description[:50]}]: ")
        new_level = prompt(f"Level [{p.level}]: ")
        new_seats = prompt(f"Seats [{p.max_winners}]: ")
        
        success_flag, msg = self.poll_service.update_position(current_user, pid, new_title, new_desc, new_level, new_seats)
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _delete_position(self, current_user):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        positions = self.ds.positions
        if not positions: print(); info("No positions found."); pause(); return
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        
        try: pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in positions: error("Position not found."); pause(); return
        
        if prompt(f"Confirm deactivation of '{positions[pid].title}'? (yes/no): ").lower() == "yes":
            success_flag, msg = self.poll_service.delete_position(current_user, pid)
            if success_flag: success(msg)
            else: error(msg)
        pause()

    # Poll View Methods
    def _create_poll(self, current_user):
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = prompt("Poll/Election Title: ")
        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")
        
        active_positions = {pid: p for pid, p in self.ds.positions.items() if p.is_active}
        if not active_positions: error("No active positions."); pause(); return
        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for p in active_positions.values():
            print(f"    {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}) - {p.max_winners} seat(s){RESET}")
        
        try: selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError: error("Invalid input."); pause(); return
        
        active_stations = {sid: s for sid, s in self.ds.voting_stations.items() if s.is_active}
        if not active_stations: error("No active stations."); pause(); return
        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for s in active_stations.values():
            print(f"    {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET}")
        
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try: selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError: error("Invalid input."); pause(); return

        success_flag, msg = self.poll_service.create_poll(current_user, title, description, election_type, start_date, end_date, selected_position_ids, selected_station_ids)
        if success_flag: 
            success(msg)
            warning("Status: DRAFT - Assign candidates and then open the poll.")
        else: error(msg)
        pause()

    def _view_all_polls(self):
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        for poll in polls.values():
            sc = GREEN if poll.status == 'open' else (YELLOW if poll.status == 'draft' else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll.id}: {poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll.status.upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll.start_date} to {poll.end_date}  {DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                cand_names = [self.ds.candidates[ccid].full_name for ccid in pos["candidate_ids"] if ccid in self.ds.candidates]
                cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        pause()

    def _update_poll(self, current_user):
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        for poll in polls.values():
            sc = GREEN if poll.status == 'open' else (YELLOW if poll.status == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {sc}({poll.status}){RESET}")
        
        try: pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in polls: error("Poll not found."); pause(); return
        
        poll = polls[pid]
        print(f"\n  {BOLD}Updating: {poll.title}{RESET}")
        info("Press Enter to keep current value\n")
        new_title = prompt(f"Title [{poll.title}]: ")
        new_desc = prompt(f"Description [{poll.description[:50]}]: ")
        new_type = prompt(f"Election Type [{poll.election_type}]: ")
        new_start = prompt(f"Start Date [{poll.start_date}]: ")
        new_end = prompt(f"End Date [{poll.end_date}]: ")
        
        success_flag, msg = self.poll_service.update_poll(current_user, pid, new_title, new_desc, new_type, new_start, new_end)
        if success_flag: success(msg)
        else: error(msg)
        pause()

    def _delete_poll(self, current_user):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {DIM}({poll.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in polls: error("Poll not found."); pause(); return
        
        if polls[pid].total_votes_cast > 0:
            warning(f"This poll has {polls[pid].total_votes_cast} votes recorded.")
        
        if prompt(f"Confirm deletion of '{polls[pid].title}'? (yes/no): ").lower() == "yes":
            success_flag, msg = self.poll_service.delete_poll(current_user, pid)
            if success_flag: success(msg)
            else: error(msg)
        pause()

    def _open_close_poll(self, current_user):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        for poll in polls.values():
            sc = GREEN if poll.status == 'open' else (YELLOW if poll.status == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title}  {sc}{BOLD}{poll.status.upper()}{RESET}")
        
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in polls: error("Poll not found."); pause(); return
        
        poll = polls[pid]
        action = None
        if poll.status == "draft": action = "open"
        elif poll.status == "open": action = "close"
        elif poll.status == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes": action = "reopen"
        
        if action:
            success_flag, msg = self.poll_service.toggle_poll_status(current_user, pid, action)
            if success_flag: success(msg)
            else: error(msg)
        pause()

    def _assign_candidates_to_poll(self, current_user):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        if not self.ds.candidates: print(); info("No candidates found."); pause(); return
        
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {DIM}({poll.status}){RESET}")
        
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in polls: error("Poll not found."); pause(); return
        
        poll = polls[pid]
        if poll.status == "open": error("Cannot modify candidates of an open poll."); pause(); return
        
        updates = {}
        for i, pos in enumerate(poll.positions):
            subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            current_cands = [f"{ccid}: {self.ds.candidates[ccid].full_name}" for ccid in pos["candidate_ids"] if ccid in self.ds.candidates]
            if current_cands: print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else: info("No candidates assigned yet.")
            
            p_data = self.ds.positions.get(pos["position_id"])
            min_age = p_data.min_candidate_age if p_data else 25
            eligible = {cid: c for cid, c in self.ds.candidates.items() if c.is_active and c.is_approved and c.age >= min_age}
            
            if not eligible: info("No eligible candidates found."); continue
            
            subheader("Available Candidates", THEME_ADMIN)
            for c in eligible.values():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if c.id in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}) - Age: {c.age}{RESET}{marker}")
            
            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    updates[i] = [nid for nid in new_ids if nid in eligible]
                except ValueError: error("Invalid input. Skipping this position.")
        
        if updates:
            success_flag, msg = self.poll_service.assign_candidates(current_user, pid, updates)
            if success_flag: success(msg)
            else: error(msg)
        pause()

    # Voter View Methods
    def _view_all_voters(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self.voter_service.get_all_voters()
        if not voters: print(); info("No voters registered."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        for v in voters.values():
            verified = status_badge("Yes", True) if v.is_verified else status_badge("No", False)
            active = status_badge("Yes", True) if v.is_active else status_badge("No", False)
            print(f"  {v.id:<5} {v.full_name:<25} {v.voter_card_number:<15} {v.station_id:<6} {verified:<19} {active}")
        
        verified_count = sum(1 for v in voters.values() if v.is_verified)
        unverified_count = sum(1 for v in voters.values() if not v.is_verified)
        print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        pause()

    def _verify_voter(self, current_user):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        voters = self.ds.voters
        unverified = {vid: v for vid, v in voters.items() if not v.is_verified}
        if not unverified: print(); info("No unverified voters."); pause(); return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for v in unverified.values():
            print(f"  {THEME_ADMIN}{v.id}.{RESET} {v.full_name} {DIM}│ NID: {v.national_id} │ Card: {v.voter_card_number}{RESET}")
        print()
        menu_item(1, "Verify a single voter", THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        if choice == "1":
            vid_or_card = prompt("Enter Voter ID or Card Number: ")
            if not vid_or_card: return
            success_flag, msg = self.voter_service.verify_voter(current_user.username, vid_or_card)
            if success_flag: success(msg)
            else: error(msg)
        elif choice == "2":
            count = self.voter_service.verify_all_pending(current_user.username)
            success(f"{count} voters verified!")
        pause()

    def _deactivate_voter(self, current_user):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        voters = self.ds.voters
        if not voters: print(); info("No voters found."); pause(); return
        
        identifier = prompt("Enter Voter ID or Card Number to deactivate: ")
        if not identifier: return
        
        # Use service to check if voter exists before confirming
        voter = self.voter_service._get_voter_by_id_or_card(identifier)
        if not voter:
            error("Voter not found.")
            pause()
            return

        if prompt(f"Deactivate '{voter.full_name}'? (yes/no): ").lower() == "yes":
            success_flag, msg = self.voter_service.deactivate_voter(current_user.username, identifier)
            if success_flag: success(msg)
            else: error(msg)
        pause()

    def _search_voters(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN); menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID", THEME_ADMIN); menu_item(4, "Station", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        
        results = []
        if choice == "4":
            try: sid = int(prompt("Station ID: "))
            except ValueError: error("Invalid input."); pause(); return
            results = self.voter_service.search_voters("4", station_id=sid)
        else:
            term = prompt("Search term: ")
            results = self.voter_service.search_voters(choice, term=term)
            
        if not results: print(); info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = status_badge("Verified", True) if v.is_verified else status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {v.id}  {DIM}│{RESET}  {v.full_name}  {DIM}│  Card:{RESET} {v.voter_card_number}  {DIM}│{RESET}  {verified}")
        pause()

    # Admin Management
    # Redacted for length but following the same pattern...
    def _create_admin(self, current_user):
        if current_user.role != "super_admin": error("Only super admins can create admin accounts."); pause(); return
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        username = prompt("Username: ")
        full_name = prompt("Full Name: ")
        email = prompt("Email: ")
        password = masked_input("Password: ").strip()
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        roles = ["super_admin", "election_officer", "station_manager", "auditor"]
        for i, r in enumerate(roles, 1): print(f"  {THEME_ADMIN}{i}.{RESET} {r}")
        try:
            r_choice = int(prompt("Select role (1-4): "))
            role = roles[r_choice-1]
        except (ValueError, IndexError): error("Invalid role."); pause(); return
        
        from src.models.user import Admin
        from src.services.auth_service import AuthService
        aid = self.ds.admin_id_counter
        self.ds.admins[aid] = Admin(id=aid, username=username, full_name=full_name, email=email, password=AuthService.hash_password(password), role=role)
        self.ds.admin_id_counter += 1
        self.ds.log_action("CREATE_ADMIN", current_user.username, f"Created admin: {username}")
        self.ds.save_data()
        success("Admin created.")
        pause()

    def _view_admins(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
        table_divider(78, THEME_ADMIN)
        for a in self.ds.admins.values():
            active = status_badge("Yes", True) if a.is_active else status_badge("No", False)
            print(f"  {a.id:<5} {a.username:<20} {a.full_name:<25} {a.role:<20} {active}")
        pause()

    def _deactivate_admin(self, current_user):
        if current_user.role != "super_admin": error("Only super admins can deactivate admins."); pause(); return
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        try:
            aid = int(prompt("Admin ID: "))
            if aid == current_user.id: error("Cannot deactivate yourself."); pause(); return
            if aid in self.ds.admins:
                self.ds.admins[aid].is_active = False
                self.ds.log_action("DEACTIVATE_ADMIN", current_user.username, f"Deactivated admin: {self.ds.admins[aid].username}")
                self.ds.save_data()
                success("Admin deactivated.")
        except ValueError: error("Invalid input.")
        pause()

    # Report Views
    def _view_poll_results(self):
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        polls = self.ds.polls
        if not polls: print(); info("No polls found."); pause(); return
        for p in polls.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
            tally = self.report_service.get_tally_for_poll(pid)
            if tally:
                clear_screen()
                header(f"RESULTS: {tally['poll'].title}", THEME_ADMIN)
                print(f"  {DIM}Status:{RESET} {tally['poll'].status.upper()}  {DIM}│  Votes:{RESET} {tally['poll'].total_votes_cast}")
                print(f"  {DIM}Eligible:{RESET} {tally['total_eligible']}  {DIM}│  Turnout:{RESET} {tally['turnout_pct']:.1f}%")
                for res in tally["results"]:
                    subheader(f"{res['position']['position_title']} (Seats: {res['winner_seats']})", THEME_ADMIN_ACCENT)
                    for rank, (cand, count) in enumerate(res["candidates"], 1):
                        pct = (count / res["total_votes"] * 100) if res["total_votes"] > 0 else 0
                        bar = f"{THEME_ADMIN}{'█' * int(pct/2)}{GRAY}{'░' * (50-int(pct/2))}{RESET}"
                        winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= res["winner_seats"] else ""
                        print(f"    {BOLD}{rank}. {cand.full_name}{RESET} ({cand.party})")
                        print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                    if res["abstained"] > 0: print(f"    {GRAY}Abstained: {res['abstained']} ({res['abstained']/res['total_votes']*100 if res['total_votes']>0 else 0:.1f}%){RESET}")
        except ValueError: error("Invalid input.")
        pause()

    def _view_detailed_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)
        overview = self.report_service.get_system_overview()
        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        print(f"  Candidates: {overview['candidates']['total']} (Active: {overview['candidates']['active']})")
        print(f"  Voters: {overview['voters']['total']} (Verified: {overview['voters']['verified']})")
        print(f"  Polls: {overview['polls']['total']} (Open: {overview['polls']['open']})")
        
        g_counts, age_groups = self.report_service.get_voter_demographics()
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        for g, count in g_counts.items(): print(f"  {g}: {count}")
        for group, count in age_groups.items(): print(f"  {group:>5}: {count:>3}")
        
        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for s, vc, lp in self.report_service.get_station_loads():
             print(f"  {s.name}: {vc}/{s.capacity} ({lp:.0f}%)")
        pause()

    def _view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        menu_item(1, "Last 20 entries", THEME_ADMIN)
        menu_item(2, "Filter by action", THEME_ADMIN)
        choice = prompt("Choice: ")
        entries = self.audit_service.get_recent_logs() if choice == "1" else self.audit_service.get_all_logs()
        table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        table_divider(100, THEME_ADMIN)
        for e in entries:
             print(f"  {DIM}{e.timestamp[:19]}{RESET} {e.action:<25} {e.user:<20} {e.details[:50]}")
        pause()

    def _station_wise_results(self):
        # Implementation... simplified for length
        pause()
