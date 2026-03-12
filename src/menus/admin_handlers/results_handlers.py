"""Admin menu: Results and reports (Poll results, statistics, audit log, station-wise results)."""
from src.config.constants import (
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    DIM,
    BOLD,
    RESET,
    GREEN,
    YELLOW,
    RED,
    GRAY,
    BG_GREEN,
    BLACK,
    BRIGHT_WHITE,
)
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminResultsHandlers(AdminHandlerBase):
    """Handles admin options 27–30: results, statistics, audit log, station-wise results."""

    def view_poll_results(self) -> None:
        self.clear_screen()
        self.ui.header("POLL RESULTS", THEME_ADMIN)
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
        print()
        self.ui.header(f"RESULTS: {poll['title']}", THEME_ADMIN)
        sc = GREEN if poll["status"] == "open" else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
        total_eligible = sum(
            1 for v in self.repo.voters.values()
            if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"]
        )
        turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
        for pos in poll["positions"]:
            self.ui.subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
            vote_counts = {}
            abstain_count = 0
            total_pos = 0
            for v in self.repo.votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    total_pos += 1
                    if v["abstained"]:
                        abstain_count += 1
                    else:
                        vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = self.repo.candidates.get(cid, {})
                pct = (count / total_pos * 100) if total_pos > 0 else 0
                bl = int(pct / 2)
                bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
            if not vote_counts:
                self.info("    No votes recorded for this position.")
        self.pause()

    def view_detailed_statistics(self) -> None:
        self.clear_screen()
        self.ui.header("DETAILED STATISTICS", THEME_ADMIN)
        self.ui.subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        tc = len(self.repo.candidates)
        ac = sum(1 for c in self.repo.candidates.values() if c["is_active"])
        tv = len(self.repo.voters)
        vv = sum(1 for v in self.repo.voters.values() if v["is_verified"])
        av = sum(1 for v in self.repo.voters.values() if v["is_active"])
        ts = len(self.repo.voting_stations)
        ast = sum(1 for s in self.repo.voting_stations.values() if s["is_active"])
        tp = len(self.repo.polls)
        op = sum(1 for p in self.repo.polls.values() if p["status"] == "open")
        cp = sum(1 for p in self.repo.polls.values() if p["status"] == "closed")
        dp = sum(1 for p in self.repo.polls.values() if p["status"] == "draft")
        print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(self.repo.votes)}")
        self.ui.subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in self.repo.voters.values():
            gender_counts[v.get("gender", "?")] = gender_counts.get(v.get("gender", "?"), 0) + 1
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
        self.ui.subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for sid, s in self.repo.voting_stations.items():
            vc = sum(1 for v in self.repo.voters.values() if v["station_id"] == sid)
            lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
        self.ui.subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        party_counts = {}
        for c in self.repo.candidates.values():
            if c["is_active"]:
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
        self.ui.subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        edu_counts = {}
        for c in self.repo.candidates.values():
            if c["is_active"]:
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
        for edu, count in edu_counts.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        self.pause()

    def view_audit_log(self) -> None:
        self.clear_screen()
        self.ui.header("AUDIT LOG", THEME_ADMIN)
        if not self.repo.audit_log:
            print()
            self.info("No audit records.")
            self.pause()
            return
        print(f"\n  {DIM}Total Records: {len(self.repo.audit_log)}{RESET}")
        self.ui.subheader("Filter", THEME_ADMIN_ACCENT)
        self.ui.menu_item(1, "Last 20 entries", THEME_ADMIN)
        self.ui.menu_item(2, "All entries", THEME_ADMIN)
        self.ui.menu_item(3, "Filter by action type", THEME_ADMIN)
        self.ui.menu_item(4, "Filter by user", THEME_ADMIN)
        choice = self.prompt("\nChoice: ")
        if choice == "1":
            entries = self.audit.get_audit_entries("1")
        elif choice == "2":
            entries = self.audit.get_audit_entries("2")
        elif choice == "3":
            action_types = self.audit.get_action_types()
            for i, at in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                at_choice = int(self.prompt("Select action type (number): "))
                action_types_list = list(action_types)
                if 1 <= at_choice <= len(action_types_list):
                    entries = self.audit.get_audit_entries("3", action_types_list[at_choice - 1])
                else:
                    self.error("Invalid choice.")
                    self.pause()
                    return
            except (ValueError, IndexError):
                self.error("Invalid choice.")
                self.pause()
                return
        elif choice == "4":
            uf = self.prompt("Enter username/card number: ")
            entries = self.audit.get_audit_entries("4", uf)
        else:
            self.error("Invalid choice.")
            self.pause()
            return
        print()
        self.ui.table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        self.ui.table_divider(100, THEME_ADMIN)
        for entry in entries:
            ac = (
                GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN"
                else (RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]
                      else (YELLOW if "UPDATE" in entry["action"] else RESET))
            )
            print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET} {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
        self.pause()

    def station_wise_results(self) -> None:
        self.clear_screen()
        self.ui.header("STATION-WISE RESULTS", THEME_ADMIN)
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
        print()
        self.ui.header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
        for sid in poll["station_ids"]:
            if sid not in self.repo.voting_stations:
                continue
            station = self.repo.voting_stations[sid]
            self.ui.subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
            station_votes = [v for v in self.repo.votes if v["poll_id"] == pid and v["station_id"] == sid]
            svc = len(set(v["voter_id"] for v in station_votes))
            ras = sum(
                1 for v in self.repo.voters.values()
                if v["station_id"] == sid and v["is_verified"] and v["is_active"]
            )
            st = (svc / ras * 100) if ras > 0 else 0
            tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
            print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
            for pos in poll["positions"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
                pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v["abstained"]:
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                total = sum(vc.values()) + ac
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = self.repo.candidates.get(cid, {})
                    pct = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0:
                    print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
        self.pause()
