"""Admin menu: Poll and election lifecycle (Create, View, Update, Delete, Open/Close, Assign candidates)."""
from src.config.constants import (
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    DIM,
    BOLD,
    GREEN,
    YELLOW,
    RED,
    RESET,
    MIN_CANDIDATE_AGE,
)
from src.services import poll_service
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminPollHandlers(AdminHandlerBase):
    """Handles admin options 14–19: poll CRUD, open/close, assign candidates."""

    def create_poll(self) -> None:
        self.clear_screen()
        self.ui.header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = self.prompt("Poll/Election Title: ")
        if not title:
            self.error("Title cannot be empty.")
            self.pause()
            return
        description = self.prompt("Description: ")
        election_type = self.prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = self.prompt("Start Date (YYYY-MM-DD): ")
        end_date = self.prompt("End Date (YYYY-MM-DD): ")
        if not self.repo.positions:
            self.error("No positions available. Create positions first.")
            self.pause()
            return
        active_positions = {pid: p for pid, p in self.repo.positions.items() if p["is_active"]}
        if not active_positions:
            self.error("No active positions.")
            self.pause()
            return
        self.ui.subheader("Available Positions", THEME_ADMIN_ACCENT)
        for pid, p in active_positions.items():
            print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
        try:
            selected_position_ids = [int(x.strip()) for x in self.prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        position_ids = [spid for spid in selected_position_ids if spid in active_positions]
        if not position_ids:
            self.error("No valid positions selected.")
            self.pause()
            return
        if not self.repo.voting_stations:
            self.error("No voting stations. Create stations first.")
            self.pause()
            return
        active_stations = {sid: s for sid, s in self.repo.voting_stations.items() if s["is_active"]}
        self.ui.subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for sid, s in active_stations.items():
            print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
        if self.prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            station_ids = list(active_stations.keys())
        else:
            try:
                station_ids = [int(x.strip()) for x in self.prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                self.error("Invalid input.")
                self.pause()
                return
        ok, msg = poll_service.create_poll(
            self.repo, self.user["username"], title, description, election_type,
            start_date, end_date, position_ids, station_ids
        )
        if ok:
            self.audit.log_action("CREATE_POLL", self.user["username"], f"Created poll: {title} (ID: {self.repo.poll_id_counter - 1})")
            self.success(msg)
            self.warning("Status: DRAFT - Assign candidates and then open the poll.")
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def view_all_polls(self) -> None:
        self.clear_screen()
        self.ui.header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        if not self.repo.polls:
            print()
            self.info("No polls found.")
            self.pause()
            return
        for pid, poll in self.repo.polls.items():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cand_names = [self.repo.candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in self.repo.candidates]
                cand_display = ", ".join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(self.repo.polls)}{RESET}")
        self.pause()

    def update_poll(self) -> None:
        self.clear_screen()
        self.ui.header("UPDATE POLL", THEME_ADMIN)
        if not self.repo.polls:
            print()
            self.info("No polls found.")
            self.pause()
            return
        print()
        for pid, poll in self.repo.polls.items():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        try:
            pid = int(self.prompt("\nEnter Poll ID to update: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.polls:
            self.error("Poll not found.")
            self.pause()
            return
        poll = self.repo.polls[pid]
        if poll["status"] == "open":
            self.error("Cannot update an open poll. Close it first.")
            self.pause()
            return
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            self.error("Cannot update a poll with votes.")
            self.pause()
            return
        print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
        self.info("Press Enter to keep current value\n")
        new_title = self.prompt(f"Title [{poll['title']}]: ")
        new_desc = self.prompt(f"Description [{poll['description'][:50]}]: ")
        new_type = self.prompt(f"Election Type [{poll['election_type']}]: ")
        new_start = self.prompt(f"Start Date [{poll['start_date']}]: ")
        new_end = self.prompt(f"End Date [{poll['end_date']}]: ")
        ok, msg = poll_service.update_poll(
            self.repo, pid, self.user["username"],
            title=new_title or None, description=new_desc if new_desc else None,
            election_type=new_type or None, start_date=new_start or None, end_date=new_end or None
        )
        if ok:
            self.audit.log_action("UPDATE_POLL", self.user["username"], f"Updated poll: {poll['title']}")
            self.success("Poll updated!")
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def delete_poll(self) -> None:
        self.clear_screen()
        self.ui.header("DELETE POLL", THEME_ADMIN)
        if not self.repo.polls:
            print()
            self.info("No polls found.")
            self.pause()
            return
        print()
        for pid, poll in self.repo.polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(self.prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.polls:
            self.error("Poll not found.")
            self.pause()
            return
        if self.repo.polls[pid]["status"] == "open":
            self.error("Cannot delete an open poll. Close it first.")
            self.pause()
            return
        if self.repo.polls[pid]["total_votes_cast"] > 0:
            self.warning(f"This poll has {self.repo.polls[pid]['total_votes_cast']} votes recorded.")
        if self.prompt(f"Confirm deletion of '{self.repo.polls[pid]['title']}'? (yes/no): ").lower() == "yes":
            ok, msg = poll_service.delete_poll(self.repo, pid, self.user["username"])
            if ok:
                self.audit.log_action("DELETE_POLL", self.user["username"], msg)
                self.success(msg)
                self.repo.save()
            else:
                self.error(msg)
        self.pause()

    def open_close_poll(self) -> None:
        self.clear_screen()
        self.ui.header("OPEN / CLOSE POLL", THEME_ADMIN)
        if not self.repo.polls:
            print()
            self.info("No polls found.")
            self.pause()
            return
        print()
        for pid, poll in self.repo.polls.items():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
        try:
            pid = int(self.prompt("\nEnter Poll ID: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.polls:
            self.error("Poll not found.")
            self.pause()
            return
        poll = self.repo.polls[pid]
        if poll["status"] == "draft":
            if not any(pos["candidate_ids"] for pos in poll["positions"]):
                self.error("Cannot open - no candidates assigned.")
                self.pause()
                return
            if self.prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
                ok, msg = poll_service.open_poll(self.repo, pid, self.user["username"])
                if ok:
                    self.audit.log_action("OPEN_POLL", self.user["username"], f"Opened poll: {poll['title']}")
                    self.success(msg)
                    self.repo.save()
                else:
                    self.error(msg)
        elif poll["status"] == "open":
            if self.prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                ok, msg = poll_service.close_poll(self.repo, pid, self.user["username"])
                if ok:
                    self.audit.log_action("CLOSE_POLL", self.user["username"], f"Closed poll: {poll['title']}")
                    self.success(msg)
                    self.repo.save()
                else:
                    self.error(msg)
        elif poll["status"] == "closed":
            self.info("This poll is already closed.")
            if self.prompt("Reopen it? (yes/no): ").lower() == "yes":
                ok, msg = poll_service.reopen_poll(self.repo, pid, self.user["username"])
                if ok:
                    self.audit.log_action("REOPEN_POLL", self.user["username"], f"Reopened poll: {poll['title']}")
                    self.success(msg)
                    self.repo.save()
                else:
                    self.error(msg)
        self.pause()

    def assign_candidates_to_poll(self) -> None:
        self.clear_screen()
        self.ui.header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        if not self.repo.polls:
            print()
            self.info("No polls found.")
            self.pause()
            return
        if not self.repo.candidates:
            print()
            self.info("No candidates found.")
            self.pause()
            return
        print()
        for pid, poll in self.repo.polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(self.prompt("\nEnter Poll ID: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.polls:
            self.error("Poll not found.")
            self.pause()
            return
        poll = self.repo.polls[pid]
        if poll["status"] == "open":
            self.error("Cannot modify candidates of an open poll.")
            self.pause()
            return
        for i, pos in enumerate(poll["positions"]):
            self.ui.subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            current_cands = [f"{ccid}: {self.repo.candidates[ccid]['full_name']}" for ccid in pos["candidate_ids"] if ccid in self.repo.candidates]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                self.info("No candidates assigned yet.")
            active_candidates = {cid: c for cid, c in self.repo.candidates.items() if c["is_active"] and c.get("is_approved", True)}
            pos_data = self.repo.positions.get(pos["position_id"], {})
            min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
            eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
            if not eligible:
                self.info("No eligible candidates found.")
                continue
            self.ui.subheader("Available Candidates", THEME_ADMIN)
            for cid, c in eligible.items():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
            if self.prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_cand_ids = [int(x.strip()) for x in self.prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    ok, msg = poll_service.assign_candidates_to_poll(self.repo, pid, self.user["username"], i, new_cand_ids)
                    if ok:
                        self.success(msg)
                    else:
                        self.error(msg)
                except ValueError:
                    self.error("Invalid input. Skipping this position.")
        self.audit.log_action("ASSIGN_CANDIDATES", self.user["username"], f"Updated candidates for poll: {poll['title']}")
        self.repo.save()
        self.pause()
