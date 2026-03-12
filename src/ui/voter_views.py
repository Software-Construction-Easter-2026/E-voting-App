from src.ui.theme import *

class VoterViews:
    def __init__(self, services):
        self.services = services
        self.voter_service = services['voter']
        self.voting_service = services['voting']
        self.report_service = services['report']
        self.ds = services['data_store']

    def dashboard(self, current_user):
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            station = self.ds.voting_stations.get(current_user.station_id)
            station_name = station.name if station else "Unknown"
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user.full_name}{RESET}")
            print(f"  {DIM}    Card: {current_user.voter_card_number}  │  Station: {station_name}{RESET}")
            print()
            
            menu_item(1, "View Open Polls", THEME_VOTER)
            menu_item(2, "Cast Vote", THEME_VOTER)
            menu_item(3, "View My Voting History", THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
            menu_item(5, "View My Profile", THEME_VOTER)
            menu_item(6, "Change Password", THEME_VOTER)
            menu_item(7, "Logout", THEME_VOTER)
            print()
            
            choice = prompt("Enter choice: ")
            if choice == "1": self._view_open_polls(current_user)
            elif choice == "2": self._cast_vote(current_user)
            elif choice == "3": self._view_voting_history(current_user)
            elif choice == "4": self._view_closed_results()
            elif choice == "5": self._view_profile(current_user)
            elif choice == "6": self._change_password(current_user)
            elif choice == "7":
                self.ds.log_action("LOGOUT", current_user.voter_card_number, "Voter logged out")
                self.ds.save_data()
                break
            else: error("Invalid choice."); pause()

    def _view_open_polls(self, current_user):
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        open_polls = [p for p in self.ds.polls.values() if p.status == "open"]
        if not open_polls: info("No open polls."); pause(); return
        
        for poll in open_polls:
            already_voted = poll.id in current_user.has_voted_in
            vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll.id}: {poll.title}{RESET}{vs}")
            for pos in poll.positions:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for ccid in pos["candidate_ids"]:
                    c = self.ds.candidates.get(ccid)
                    if c: print(f"      {DIM}•{RESET} {c.full_name} ({c.party})")
        pause()

    def _cast_vote(self, current_user):
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        available_polls = [p for p in self.ds.polls.values() if p.status == "open" 
                           and p.id not in current_user.has_voted_in 
                           and current_user.station_id in p.station_ids]
        
        if not available_polls: info("No available polls to vote in."); pause(); return
        
        for p in available_polls:
            print(f"  {THEME_VOTER}{p.id}.{RESET} {p.title}")
            
        try: pid = int(prompt("\nSelect Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        
        poll = next((p for p in available_polls if p.id == pid), None)
        if not poll: error("Invalid selection."); pause(); return
        
        my_votes = []
        for pos in poll.positions:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            cands = [self.ds.candidates[ccid] for ccid in pos["candidate_ids"] if ccid in self.ds.candidates]
            for idx, c in enumerate(cands, 1):
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c.full_name} ({c.party})")
            print(f"    {GRAY}{BOLD}0.{RESET} Abstain / Skip")
            
            try: choice = int(prompt(f"Choice for {pos['position_title']}: "))
            except ValueError: choice = 0
            
            if choice == 0 or choice > len(cands):
                my_votes.append({"position_id": pos["position_id"], "candidate_id": None, "abstained": True})
            else:
                my_votes.append({"position_id": pos["position_id"], "candidate_id": cands[choice-1].id, "abstained": False})
        
        if prompt("Confirm votes? (yes/no): ").lower() == "yes":
            success_flag, v_hash = self.voting_service.cast_vote(current_user, pid, my_votes)
            if success_flag:
                success("Vote recorded!")
                print(f"  Ref: {v_hash}")
        pause()

    def _view_voting_history(self, current_user):
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        if not current_user.has_voted_in: info("No history."); pause(); return
        for pid in current_user.has_voted_in:
            poll = self.ds.polls.get(pid)
            if poll:
                print(f"  Poll: {poll.title}")
                # Filter votes for this user/poll
                my_records = [v for v in self.ds.votes if v.poll_id == pid and v.voter_id == current_user.id]
                for vr in my_records:
                    p_title = next((p['position_title'] for p in poll.positions if p['position_id'] == vr.position_id), "Unknown")
                    c_name = self.ds.candidates[vr.candidate_id].full_name if not vr.abstained and vr.candidate_id in self.ds.candidates else "Abstained"
                    print(f"    - {p_title}: {c_name}")
        pause()

    def _view_closed_results(self):
        closed_polls = [p for p in self.ds.polls.values() if p.status == "closed"]
        if not closed_polls: info("No closed polls."); pause(); return
        for p in closed_polls:
            tally = self.report_service.get_tally_for_poll(p.id)
            if tally:
                print(f"\n  {BOLD}{tally['poll'].title}{RESET}")
                for res in tally["results"]:
                    print(f"    {res['position']['position_title']}:")
                    for cand, count in res["candidates"]:
                        print(f"      {cand.full_name}: {count}")
        pause()

    def _view_profile(self, current_user):
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        v = current_user
        fields = [("Name", v.full_name), ("Card #", v.voter_card_number), ("NID", v.national_id), ("Age", v.age)]
        for label, val in fields:
            print(f"  {THEME_VOTER}{label + ':':<10}{RESET} {val}")
        pause()

    def _change_password(self, current_user):
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        old = masked_input("Old Password: ")
        new = masked_input("New Password: ")
        confirm = masked_input("Confirm: ")
        if new != confirm: error("Match error."); pause(); return
        
        success_flag, msg = self.voter_service.change_password(current_user.id, old, new)
        if success_flag: success(msg)
        else: error(msg)
        pause()
