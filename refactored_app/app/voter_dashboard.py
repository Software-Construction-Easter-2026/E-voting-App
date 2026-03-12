"""Voter dashboard: menu loop and voter feature handlers."""

from ui import console
from ui.themes import (
    THEME_VOTER,
    THEME_VOTER_ACCENT,
    GREEN,
    RED,
    DIM,
    BOLD,
    GRAY,
    BRIGHT_GREEN,
    BRIGHT_CYAN,
    BRIGHT_YELLOW,
    ITALIC,
)
from services import auth_service, audit_service
from services import candidate_service, station_service
from services import voter_service, voting_service
from data.context import DataContext

RESET = "\033[0m"


def run(ctx: DataContext):
    while True:
        console.clear_screen()
        console.header("VOTER DASHBOARD", THEME_VOTER)
        user = auth_service.current_user
        station = station_service.get_by_id(ctx, user.get("station_id"))
        station_name = station.get("name", "Unknown") if station else "Unknown"
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{user['full_name']}{RESET}")
        print(f"  {DIM}    Card: {user['voter_card_number']}  │  Station: {station_name}{RESET}")
        print()
        console.menu_item(1, "View Open Polls", THEME_VOTER)
        console.menu_item(2, "Cast Vote", THEME_VOTER)
        console.menu_item(3, "View My Voting History", THEME_VOTER)
        console.menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
        console.menu_item(5, "View My Profile", THEME_VOTER)
        console.menu_item(6, "Change Password", THEME_VOTER)
        console.menu_item(7, "Logout", THEME_VOTER)
        print()
        choice = console.prompt("Enter choice: ")
        if choice == "1":
            _view_open_polls(ctx)
        elif choice == "2":
            _cast_vote(ctx)
        elif choice == "3":
            _view_voting_history(ctx)
        elif choice == "4":
            _view_closed_poll_results(ctx)
        elif choice == "5":
            _view_voter_profile(ctx)
        elif choice == "6":
            _change_password(ctx)
        elif choice == "7":
            audit_service.log_action(ctx, "LOGOUT", user["voter_card_number"], "Voter logged out")
            ctx.store.save()
            auth_service.clear_session()
            return
        else:
            console.error("Invalid choice.")
            console.pause()


def _view_open_polls(ctx: DataContext):
    console.clear_screen()
    console.header("OPEN POLLS", THEME_VOTER)
    open_polls = voting_service.get_all_open_polls_for_display(ctx)
    if not open_polls:
        print()
        console.info("No open polls at this time.")
        console.pause()
        return
    user = auth_service.current_user
    has_voted_in = user.get("has_voted_in") or []
    candidates = candidate_service.get_all(ctx)
    for pid, poll in open_polls.items():
        already_voted = pid in has_voted_in
        vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {THEME_VOTER_ACCENT}[NOT YET VOTED]{RESET}"
        print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
        for pos in poll.get("positions", []):
            print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
            for ccid in pos.get("candidate_ids", []):
                if ccid in candidates:
                    c = candidates[ccid]
                    print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
    console.pause()


def _cast_vote(ctx: DataContext):
    console.clear_screen()
    console.header("CAST YOUR VOTE", THEME_VOTER)
    available_polls = voting_service.get_open_polls_for_voter(ctx)
    if not available_polls:
        print()
        console.info("No available polls to vote in.")
        console.pause()
        return
    console.subheader("Available Polls", THEME_VOTER_ACCENT)
    for pid, poll in available_polls.items():
        print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
    try:
        pid = int(console.prompt("\nSelect Poll ID to vote: "))
    except ValueError:
        console.error("Invalid input.")
        console.pause()
        return
    if pid not in available_polls:
        console.error("Invalid poll selection.")
        console.pause()
        return
    poll = ctx.polls.get_by_id(pid)
    if not poll:
        console.pause()
        return
    print()
    console.header(f"Voting: {poll['title']}", THEME_VOTER)
    console.info("Please select ONE candidate for each position.\n")
    candidates = candidate_service.get_all(ctx)
    my_votes = []
    for pos in poll.get("positions", []):
        console.subheader(pos["position_title"], THEME_VOTER_ACCENT)
        cids = pos.get("candidate_ids", [])
        if not cids:
            console.info("No candidates for this position.")
            continue
        for idx, ccid in enumerate(cids, 1):
            if ccid in candidates:
                c = candidates[ccid]
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c.get('years_experience', 0)} yrs{RESET}")
                if c.get("manifesto"):
                    print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
        print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
        try:
            vote_choice = int(console.prompt(f"\nYour choice for {pos['position_title']}: "))
        except ValueError:
            console.warning("Invalid input. Skipping.")
            vote_choice = 0
        if vote_choice == 0:
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": None,
                "abstained": True,
            })
        elif 1 <= vote_choice <= len(cids):
            selected_cid = cids[vote_choice - 1]
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": selected_cid,
                "abstained": False,
            })
        else:
            console.warning("Invalid choice. Marking as abstain.")
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": None,
                "abstained": True,
            })
    console.subheader("VOTE SUMMARY", "\033[97m")
    for mv in my_votes:
        if mv["abstained"]:
            print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
        else:
            c = candidates.get(mv["candidate_id"], {})
            print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{c.get('full_name', '?')}{RESET}")
    print()
    if console.prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
        console.info("Vote cancelled.")
        console.pause()
        return
    ok, result = voting_service.cast_vote(ctx, pid, my_votes)
    if not ok:
        console.error(result)
        console.pause()
        return
    audit_service.log_action(ctx, "CAST_VOTE", auth_service.current_user["voter_card_number"], f"Voted in poll: {poll['title']} (Hash: {result})")
    print()
    console.success("Your vote has been recorded successfully!")
    print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{result}{RESET}")
    print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
    ctx.store.save()
    console.pause()


def _view_voting_history(ctx: DataContext):
    console.clear_screen()
    console.header("MY VOTING HISTORY", THEME_VOTER)
    voted_polls = voting_service.get_voting_history_for_voter(ctx)
    if not voted_polls:
        print()
        console.info("You have not voted in any polls yet.")
        console.pause()
        return
    polls = ctx.polls.get_all()
    candidates = candidate_service.get_all(ctx)
    votes_list = ctx.votes.get_all()
    user = auth_service.current_user
    print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
    for pid in voted_polls:
        if pid not in polls:
            continue
        poll = polls[pid]
        sc = GREEN if poll.get("status") == "open" else RED
        print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
        for vr in votes_list:
            if vr.get("poll_id") != pid or vr.get("voter_id") != user.get("id"):
                continue
            pos_title = next(
                (p["position_title"] for p in poll.get("positions", []) if p.get("position_id") == vr.get("position_id")),
                "Unknown",
            )
            if vr.get("abstained"):
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
            else:
                cand = candidates.get(vr.get("candidate_id"), {})
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{cand.get('full_name', 'Unknown')}{RESET}")
        print()
    console.pause()


def _view_closed_poll_results(ctx: DataContext):
    console.clear_screen()
    console.header("ELECTION RESULTS", THEME_VOTER)
    polls = ctx.polls.get_all()
    closed_polls = {pid: p for pid, p in polls.items() if p.get("status") == "closed"}
    if not closed_polls:
        print()
        console.info("No closed polls with results.")
        console.pause()
        return
    candidates = candidate_service.get_all(ctx)
    for pid, poll in closed_polls.items():
        print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll.get('total_votes_cast', 0)}")
        result = voting_service.get_poll_results(ctx, pid)
        if not result:
            continue
        for pr in result["positions_result"]:
            pos = pr["position"]
            console.subheader(pos["position_title"], THEME_VOTER_ACCENT)
            vote_counts = pr["vote_counts"]
            abstain_count = pr["abstain_count"]
            total = pr["total"]
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                winner = f" {RESET}\033[42m\033[30m\033[1m WINNER {RESET}" if rank <= pos.get("max_winners", 1) else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
    console.pause()


def _view_voter_profile(ctx: DataContext):
    console.clear_screen()
    console.header("MY PROFILE", THEME_VOTER)
    v = auth_service.current_user
    station = station_service.get_by_id(ctx, v.get("station_id"))
    station_name = station.get("name", "Unknown") if station else "Unknown"
    print()
    for label, value in [
        ("Name", v["full_name"]),
        ("National ID", v["national_id"]),
        ("Voter Card", f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
        ("Date of Birth", v["date_of_birth"]),
        ("Age", v["age"]),
        ("Gender", v["gender"]),
        ("Address", v["address"]),
        ("Phone", v["phone"]),
        ("Email", v["email"]),
        ("Station", station_name),
        ("Verified", console.status_badge("Yes", True) if v.get("is_verified") else console.status_badge("No", False)),
        ("Registered", v.get("registered_at", "")),
        ("Polls Voted", len(v.get("has_voted_in", []))),
    ]:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
    console.pause()


def _change_password(ctx: DataContext):
    console.clear_screen()
    console.header("CHANGE PASSWORD", THEME_VOTER)
    print()
    old_pass = console.masked_input("Current Password: ").strip()
    if auth_service.hash_password(old_pass) != auth_service.current_user.get("password"):
        console.error("Incorrect current password.")
        console.pause()
        return
    while True:
        new_pass = console.masked_input("New Password: ").strip()
        if len(new_pass) < 6:
            console.error("Password must be at least 6 characters.")
            continue
        confirm_pass = console.masked_input("Confirm New Password: ").strip()
        if new_pass != confirm_pass:
            console.error("Passwords do not match.")
            continue
        break
    hashed = auth_service.hash_password(new_pass)
    auth_service.current_user["password"] = hashed
    voter_service.update_password(ctx, auth_service.current_user["id"], hashed)
    audit_service.log_action(ctx, "CHANGE_PASSWORD", auth_service.current_user["voter_card_number"], "Password changed")
    print()
    console.success("Password changed successfully!")
    ctx.store.save()
    console.pause()
