from evoting.core.colors import (
    BOLD,
    BRIGHT_CYAN,
    BRIGHT_GREEN,
    BRIGHT_YELLOW,
    DIM,
    GRAY,
    GREEN,
    ITALIC,
    RED,
    RESET,
    THEME_VOTER,
    THEME_VOTER_ACCENT,
)
from evoting.ui import console_io, display


def run_voter_dashboard(ctx):
    voter = ctx.auth.current_user
    station_name = ctx.repo.voting_stations.get(voter["station_id"], {}).get("name", "Unknown")
    while True:
        console_io.clear_screen()
        display.header("VOTER DASHBOARD", THEME_VOTER)
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{voter['full_name']}{RESET}")
        print(f"  {DIM}    Card: {voter['voter_card_number']}  │  Station: {station_name}{RESET}")
        print()
        display.menu_item(1, "View Open Polls", THEME_VOTER)
        display.menu_item(2, "Cast Vote", THEME_VOTER)
        display.menu_item(3, "View My Voting History", THEME_VOTER)
        display.menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
        display.menu_item(5, "View My Profile", THEME_VOTER)
        display.menu_item(6, "Change Password", THEME_VOTER)
        display.menu_item(7, "Logout", THEME_VOTER)
        print()
        choice = console_io.prompt("Enter choice: ")
        if choice == "1":
            view_open_polls(ctx)
        elif choice == "2":
            cast_vote(ctx)
        elif choice == "3":
            view_voting_history(ctx)
        elif choice == "4":
            view_closed_poll_results(ctx)
        elif choice == "5":
            view_voter_profile(ctx)
        elif choice == "6":
            change_voter_password(ctx)
        elif choice == "7":
            ctx.auth.logout()
            try:
                ctx.repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
            break
        else:
            display.error("Invalid choice.")
            console_io.pause()


def view_open_polls(ctx):
    vote_svc = ctx.vote_svc
    candidate_svc = ctx.candidate_svc
    voter = ctx.auth.current_user
    open_polls = vote_svc.get_open_polls()
    console_io.clear_screen()
    display.header("OPEN POLLS", THEME_VOTER)
    if not open_polls:
        print()
        display.info("No open polls at this time.")
        console_io.pause()
        return
    candidates = candidate_svc.get_all()
    for pid, poll in open_polls.items():
        already_voted = pid in voter.get("has_voted_in", [])
        vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {BOLD}[NOT YET VOTED]{RESET}"
        print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
        for pos in poll["positions"]:
            print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
            for ccid in pos["candidate_ids"]:
                if ccid in candidates:
                    c = candidates[ccid]
                    print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
    console_io.pause()


def cast_vote(ctx):
    repo, auth, vote_svc, candidate_svc = ctx.repo, ctx.auth, ctx.vote_svc, ctx.candidate_svc
    voter = auth.current_user
    available_polls = vote_svc.get_available_polls_for_voter(voter)
    console_io.clear_screen()
    display.header("CAST YOUR VOTE", THEME_VOTER)
    if not available_polls:
        print()
        display.info("No available polls to vote in.")
        console_io.pause()
        return
    display.subheader("Available Polls", THEME_VOTER_ACCENT)
    for pid, poll in available_polls.items():
        print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
    try:
        pid = int(console_io.prompt("\nSelect Poll ID to vote: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if pid not in available_polls:
        display.error("Invalid poll selection.")
        console_io.pause()
        return
    poll = repo.polls[pid]
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header(f"Voting: {poll['title']}", THEME_VOTER)
    display.info("Please select ONE candidate for each position.\n")
    my_votes = []
    for pos in poll["positions"]:
        display.subheader(pos["position_title"], THEME_VOTER_ACCENT)
        if not pos["candidate_ids"]:
            display.info("No candidates for this position.")
            continue
        for idx, ccid in enumerate(pos["candidate_ids"], 1):
            if ccid in candidates:
                c = candidates[ccid]
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                if c.get("manifesto"):
                    print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
        print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
        try:
            vote_choice = int(console_io.prompt(f"\nYour choice for {pos['position_title']}: "))
        except ValueError:
            display.warning("Invalid input. Skipping.")
            vote_choice = 0
        if vote_choice == 0:
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": None,
                "abstained": True,
            })
        elif 1 <= vote_choice <= len(pos["candidate_ids"]):
            selected_cid = pos["candidate_ids"][vote_choice - 1]
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": selected_cid,
                "candidate_name": candidates[selected_cid]["full_name"],
                "abstained": False,
            })
        else:
            display.warning("Invalid choice. Marking as abstain.")
            my_votes.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "candidate_id": None,
                "abstained": True,
            })
    display.subheader("VOTE SUMMARY", RESET)
    for mv in my_votes:
        if mv["abstained"]:
            print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
        else:
            print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
    print()
    if console_io.prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
        display.info("Vote cancelled.")
        console_io.pause()
        return
    vote_choices = [
        {
            "position_id": mv["position_id"],
            "candidate_id": mv.get("candidate_id"),
            "abstained": mv.get("abstained", False),
        }
        for mv in my_votes
    ]
    ok, result = vote_svc.cast_vote(voter, pid, vote_choices, voter["voter_card_number"])
    if not ok:
        display.error("Vote could not be recorded.")
        console_io.pause()
        return
    print()
    display.success("Your vote has been recorded successfully!")
    print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{result}{RESET}")
    print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_voting_history(ctx):
    repo, auth, candidate_svc = ctx.repo, ctx.auth, ctx.candidate_svc
    voter = auth.current_user
    voted_polls = voter.get("has_voted_in", [])
    console_io.clear_screen()
    display.header("MY VOTING HISTORY", THEME_VOTER)
    if not voted_polls:
        print()
        display.info("You have not voted in any polls yet.")
        console_io.pause()
        return
    candidates = candidate_svc.get_all()
    print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
    for pid in voted_polls:
        if pid in repo.polls:
            poll = repo.polls[pid]
            sc = GREEN if poll["status"] == "open" else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
            for vr in [v for v in repo.votes if v["poll_id"] == pid and v["voter_id"] == voter["id"]]:
                pos_title = next(
                    (pos["position_title"] for pos in poll.get("positions", []) if pos["position_id"] == vr["position_id"]),
                    "Unknown",
                )
                if vr.get("abstained"):
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
            print()
    console_io.pause()


def view_closed_poll_results(ctx):
    repo, results_svc, candidate_svc = ctx.repo, ctx.results_svc, ctx.candidate_svc
    closed_polls = {pid: p for pid, p in repo.polls.items() if p["status"] == "closed"}
    console_io.clear_screen()
    display.header("ELECTION RESULTS", THEME_VOTER)
    if not closed_polls:
        print()
        display.info("No closed polls with results.")
        console_io.pause()
        return
    candidates = candidate_svc.get_all()
    for pid, poll in closed_polls.items():
        print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        result = results_svc.get_poll_results(pid)
        if not result:
            continue
        for item in result["positions"]:
            pos = item["position"]
            display.subheader(pos["position_title"], THEME_VOTER_ACCENT)
            total = item["total"]
            from evoting.core.colors import BG_GREEN, BLACK
            for rank, (cid, count) in enumerate(item["sorted_candidates"]):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank < pos["max_winners"] else ""
                print(f"    {BOLD}{cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if item["abstain_count"] > 0:
                print(f"    {GRAY}Abstained: {item['abstain_count']} ({(item['abstain_count'] / total * 100) if total > 0 else 0:.1f}%){RESET}")
    console_io.pause()


def view_voter_profile(ctx):
    voter = ctx.auth.current_user
    station_name = ctx.repo.voting_stations.get(voter["station_id"], {}).get("name", "Unknown")
    console_io.clear_screen()
    display.header("MY PROFILE", THEME_VOTER)
    print()
    for label, value in [
        ("Name", voter["full_name"]),
        ("National ID", voter["national_id"]),
        ("Voter Card", f"{BRIGHT_YELLOW}{voter['voter_card_number']}{RESET}"),
        ("Date of Birth", voter["date_of_birth"]),
        ("Age", voter["age"]),
        ("Gender", voter["gender"]),
        ("Address", voter["address"]),
        ("Phone", voter["phone"]),
        ("Email", voter["email"]),
        ("Station", station_name),
        ("Verified", display.status_badge("Yes", True) if voter.get("is_verified") else display.status_badge("No", False)),
        ("Registered", voter.get("registered_at", "")),
        ("Polls Voted", len(voter.get("has_voted_in", []))),
    ]:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
    console_io.pause()


def change_voter_password(ctx):
    repo, auth, voter_svc = ctx.repo, ctx.auth, ctx.voter_svc
    voter = auth.current_user
    console_io.clear_screen()
    display.header("CHANGE PASSWORD", THEME_VOTER)
    print()
    old_pass = console_io.masked_input("Current Password: ").strip()
    if auth.hash_password(old_pass) != voter["password"]:
        display.error("Incorrect current password.")
        console_io.pause()
        return
    new_pass = console_io.masked_input("New Password: ").strip()
    if len(new_pass) < 6:
        display.error("Password must be at least 6 characters.")
        console_io.pause()
        return
    confirm_pass = console_io.masked_input("Confirm New Password: ").strip()
    if new_pass != confirm_pass:
        display.error("Passwords do not match.")
        console_io.pause()
        return
    hashed = auth.hash_password(new_pass)
    voter["password"] = hashed
    voter_svc.update_password(voter["id"], hashed)
    auth._audit.log("CHANGE_PASSWORD", voter["voter_card_number"], "Password changed")
    print()
    display.success("Password changed successfully!")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()
