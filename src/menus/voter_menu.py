"""
Voter dashboard and all voter actions. Controllers: gather input, call services, display output.
"""
from src.config.constants import (
    THEME_VOTER,
    THEME_VOTER_ACCENT,
    DIM,
    BOLD,
    GREEN,
    RED,
    YELLOW,
    GRAY,
    RESET,
    BRIGHT_WHITE,
    BRIGHT_GREEN,
    BRIGHT_YELLOW,
    BRIGHT_CYAN,
    ITALIC,
)
from src.ui import console as ui
from src.data.repository import Repository
from src.services import audit_service, voting_service


def run_voter_dashboard(repo: Repository, session: dict) -> None:
    """Main voter loop: show menu and dispatch until logout."""
    user = session["user"]
    while True:
        ui.clear_screen()
        ui.header("VOTER DASHBOARD", THEME_VOTER)
        station_name = repo.voting_stations.get(user["station_id"], {}).get("name", "Unknown")
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{user['full_name']}{RESET}")
        print(f"  {DIM}    Card: {user['voter_card_number']}  │  Station: {station_name}{RESET}")
        print()
        ui.menu_item(1, "View Open Polls", THEME_VOTER)
        ui.menu_item(2, "Cast Vote", THEME_VOTER)
        ui.menu_item(3, "View My Voting History", THEME_VOTER)
        ui.menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
        ui.menu_item(5, "View My Profile", THEME_VOTER)
        ui.menu_item(6, "Change Password", THEME_VOTER)
        ui.menu_item(7, "Logout", THEME_VOTER)
        print()
        choice = ui.prompt("Enter choice: ")
        if choice == "1":
            _view_open_polls(repo, user)
        elif choice == "2":
            _cast_vote(repo, user)
        elif choice == "3":
            _view_voting_history(repo, user)
        elif choice == "4":
            _view_closed_results(repo, user)
        elif choice == "5":
            _view_profile(repo, user)
        elif choice == "6":
            _change_password(repo, user)
        elif choice == "7":
            audit_service.log_action(repo, "LOGOUT", user["voter_card_number"], "Voter logged out")
            repo.save()
            break
        else:
            ui.error("Invalid choice.")
            ui.pause()


def _view_open_polls(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("OPEN POLLS", THEME_VOTER)
    open_polls = {pid: p for pid, p in repo.polls.items() if p["status"] == "open"}
    if not open_polls:
        print()
        ui.info("No open polls at this time.")
        ui.pause()
        return
    for pid, poll in open_polls.items():
        already_voted = pid in user.get("has_voted_in", [])
        vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
        print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
        for pos in poll["positions"]:
            print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
            for ccid in pos["candidate_ids"]:
                if ccid in repo.candidates:
                    c = repo.candidates[ccid]
                    print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
    ui.pause()


def _cast_vote(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("CAST YOUR VOTE", THEME_VOTER)
    open_polls = {pid: p for pid, p in repo.polls.items() if p["status"] == "open"}
    if not open_polls:
        print()
        ui.info("No open polls at this time.")
        ui.pause()
        return
    available_polls = {}
    for pid, poll in open_polls.items():
        if not voting_service.has_voted_in_poll(repo, user["id"], pid) and user["station_id"] in poll["station_ids"]:
            available_polls[pid] = poll
    if not available_polls:
        print()
        ui.info("No available polls to vote in.")
        ui.pause()
        return
    ui.subheader("Available Polls", THEME_VOTER_ACCENT)
    for pid, poll in available_polls.items():
        print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
    try:
        pid = int(ui.prompt("\nSelect Poll ID to vote: "))
    except ValueError:
        ui.error("Invalid input.")
        ui.pause()
        return
    if pid not in available_polls:
        ui.error("Invalid poll selection.")
        ui.pause()
        return
    poll = repo.polls[pid]
    print()
    ui.header(f"Voting: {poll['title']}", THEME_VOTER)
    ui.info("Please select ONE candidate for each position.\n")
    my_votes = []
    for pos in poll["positions"]:
        ui.subheader(pos["position_title"], THEME_VOTER_ACCENT)
        if not pos["candidate_ids"]:
            ui.info("No candidates for this position.")
            continue
        for idx, ccid in enumerate(pos["candidate_ids"], 1):
            if ccid in repo.candidates:
                c = repo.candidates[ccid]
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                if c.get("manifesto"):
                    print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
        print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
        try:
            vote_choice = int(ui.prompt(f"\nYour choice for {pos['position_title']}: "))
        except ValueError:
            ui.warning("Invalid input. Skipping.")
            vote_choice = 0
        if vote_choice == 0:
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
        elif 1 <= vote_choice <= len(pos["candidate_ids"]):
            selected_cid = pos["candidate_ids"][vote_choice - 1]
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": selected_cid,
                "candidate_name": repo.candidates[selected_cid]["full_name"],
                "abstained": False,
            })
        else:
            ui.warning("Invalid choice. Marking as abstain.")
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
    ui.subheader("VOTE SUMMARY", BRIGHT_WHITE)
    for mv in my_votes:
        if mv["abstained"]:
            print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
        else:
            print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
    print()
    if ui.prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
        ui.info("Vote cancelled.")
        ui.pause()
        return
    ok, msg, vote_hash = voting_service.cast_vote(repo, user, pid, my_votes)
    if not ok:
        ui.error(msg)
        ui.pause()
        return
    audit_service.log_action(repo, "CAST_VOTE", user["voter_card_number"], f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
    ui.success(msg)
    print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
    print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
    repo.save()
    ui.pause()


def _view_voting_history(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("MY VOTING HISTORY", THEME_VOTER)
    voted_polls = user.get("has_voted_in", [])
    if not voted_polls:
        print()
        ui.info("You have not voted in any polls yet.")
        ui.pause()
        return
    print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
    for pid in voted_polls:
        if pid in repo.polls:
            poll = repo.polls[pid]
            sc = GREEN if poll["status"] == "open" else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
            for vr in [v for v in repo.votes if v["poll_id"] == pid and v["voter_id"] == user["id"]]:
                pos_title = next((pos["position_title"] for pos in poll.get("positions", []) if pos["position_id"] == vr["position_id"]), "Unknown")
                if vr["abstained"]:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{repo.candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
            print()
    ui.pause()


def _view_closed_results(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("ELECTION RESULTS", THEME_VOTER)
    closed_polls = {pid: p for pid, p in repo.polls.items() if p["status"] == "closed"}
    if not closed_polls:
        print()
        ui.info("No closed polls with results.")
        ui.pause()
        return
    for pid, poll in closed_polls.items():
        print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            ui.subheader(pos["position_title"], THEME_VOTER_ACCENT)
            vote_counts = {}
            abstain_count = 0
            for v in repo.votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    if v["abstained"]:
                        abstain_count += 1
                    else:
                        vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            total = sum(vote_counts.values()) + abstain_count
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = repo.candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                winner = f" {GREEN} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
    ui.pause()


def _view_profile(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("MY PROFILE", THEME_VOTER)
    station_name = repo.voting_stations.get(user["station_id"], {}).get("name", "Unknown")
    print()
    for label, value in [
        ("Name", user["full_name"]),
        ("National ID", user["national_id"]),
        ("Voter Card", f"{BRIGHT_YELLOW}{user['voter_card_number']}{RESET}"),
        ("Date of Birth", user["date_of_birth"]),
        ("Age", user["age"]),
        ("Gender", user["gender"]),
        ("Address", user["address"]),
        ("Phone", user["phone"]),
        ("Email", user["email"]),
        ("Station", station_name),
        ("Verified", ui.status_badge("Yes", True) if user["is_verified"] else ui.status_badge("No", False)),
        ("Registered", user["registered_at"]),
        ("Polls Voted", len(user.get("has_voted_in", []))),
    ]:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
    ui.pause()


def _change_password(repo: Repository, user: dict) -> None:
    ui.clear_screen()
    ui.header("CHANGE PASSWORD", THEME_VOTER)
    print()
    old_pass = ui.masked_input("Current Password: ").strip()
    new_pass = ui.masked_input("New Password: ").strip()
    confirm_pass = ui.masked_input("Confirm New Password: ").strip()
    if new_pass != confirm_pass:
        ui.error("Passwords do not match.")
        ui.pause()
        return
    ok, msg = voting_service.change_voter_password(repo, user, old_pass, new_pass)
    if ok:
        audit_service.log_action(repo, "CHANGE_PASSWORD", user["voter_card_number"], "Password changed")
        ui.success(msg)
        repo.save()
    else:
        ui.error(msg)
    ui.pause()
