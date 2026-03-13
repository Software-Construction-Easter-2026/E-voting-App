"""
voter_dashboard.py - Voter-facing features matching the original e_voting_console_app.py.
All data access through DatabaseEngine.
"""
import hashlib
import datetime
from ui import (clear_screen, header, subheader, menu_item, prompt, masked_input,
                pause, error, success, warning, info, status_badge)
from colors import *
from security import hash_password


def voter_dashboard(db, current_user):
    while True:
        clear_screen()
        header("VOTER DASHBOARD", THEME_VOTER)
        stations = db.get_all("voting_stations")
        station_name = stations.get(current_user["station_id"], {}).get("name", "Unknown")
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}")
        print(f"  {DIM}    Card: {current_user['voter_card_number']}  │  Station: {station_name}{RESET}")
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
        if choice == "1": view_open_polls_voter(db, current_user)
        elif choice == "2": cast_vote(db, current_user)
        elif choice == "3": view_voting_history(db, current_user)
        elif choice == "4": view_closed_poll_results_voter(db)
        elif choice == "5": view_voter_profile(db, current_user)
        elif choice == "6": change_voter_password(db, current_user)
        elif choice == "7":
            db.log_action("LOGOUT", current_user["voter_card_number"], "Voter logged out")
            db.save(); break
        else: error("Invalid choice."); pause()


def view_open_polls_voter(db, current_user):
    clear_screen()
    header("OPEN POLLS", THEME_VOTER)
    polls = db.get_all("polls")
    candidates = db.get_all("candidates")
    open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}
    if not open_polls: print(); info("No open polls at this time."); pause(); return
    for pid, poll in open_polls.items():
        already_voted = pid in current_user.get("has_voted_in", [])
        vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
        print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
        for pos in poll["positions"]:
            print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
            for ccid in pos["candidate_ids"]:
                if ccid in candidates:
                    c = candidates[ccid]
                    print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
    pause()


def cast_vote(db, current_user):
    clear_screen()
    header("CAST YOUR VOTE", THEME_VOTER)
    polls = db.get_all("polls")
    candidates = db.get_all("candidates")
    open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}
    if not open_polls: print(); info("No open polls at this time."); pause(); return
    available = {}
    for pid, poll in open_polls.items():
        if pid not in current_user.get("has_voted_in", []) and current_user["station_id"] in poll["station_ids"]:
            available[pid] = poll
    if not available: print(); info("No available polls to vote in."); pause(); return
    subheader("Available Polls", THEME_VOTER_ACCENT)
    for pid, poll in available.items():
        print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
    try: pid = int(prompt("\nSelect Poll ID to vote: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in available: error("Invalid poll selection."); pause(); return
    poll = polls[pid]
    print()
    header(f"Voting: {poll['title']}", THEME_VOTER)
    info("Please select ONE candidate for each position.\n")
    my_votes = []
    for pos in poll["positions"]:
        subheader(pos['position_title'], THEME_VOTER_ACCENT)
        if not pos["candidate_ids"]: info("No candidates for this position."); continue
        for idx, ccid in enumerate(pos["candidate_ids"], 1):
            if ccid in candidates:
                c = candidates[ccid]
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                if c["manifesto"]: print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
        print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
        try: vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
        except ValueError: warning("Invalid input. Skipping."); vote_choice = 0
        if vote_choice == 0:
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
        elif 1 <= vote_choice <= len(pos["candidate_ids"]):
            selected_cid = pos["candidate_ids"][vote_choice - 1]
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": selected_cid, "candidate_name": candidates[selected_cid]["full_name"], "abstained": False})
        else:
            warning("Invalid choice. Marking as abstain.")
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
    subheader("VOTE SUMMARY", BRIGHT_WHITE)
    for mv in my_votes:
        if mv["abstained"]: print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
        else: print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
    print()
    if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes": info("Vote cancelled."); pause(); return
    vote_timestamp = str(datetime.datetime.now())
    vote_hash = hashlib.sha256(f"{current_user['id']}{pid}{vote_timestamp}".encode()).hexdigest()[:16]
    for mv in my_votes:
        db.append_to_list("votes", {"vote_id": vote_hash + str(mv["position_id"]), "poll_id": pid, "position_id": mv["position_id"], "candidate_id": mv["candidate_id"], "voter_id": current_user["id"], "station_id": current_user["station_id"], "timestamp": vote_timestamp, "abstained": mv["abstained"]})
    current_user["has_voted_in"].append(pid)
    voters = db.get_all("voters")
    for vid, v in voters.items():
        if v["id"] == current_user["id"]:
            db.update("voters", vid, {"has_voted_in": v.get("has_voted_in", []) + [pid]}); break
    db.update("polls", pid, {"total_votes_cast": poll["total_votes_cast"] + 1})
    db.log_action("CAST_VOTE", current_user["voter_card_number"], f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
    print()
    success("Your vote has been recorded successfully!")
    print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
    print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
    pause()


def view_voting_history(db, current_user):
    clear_screen()
    header("MY VOTING HISTORY", THEME_VOTER)
    voted_polls = current_user.get("has_voted_in", [])
    if not voted_polls: print(); info("You have not voted in any polls yet."); pause(); return
    polls = db.get_all("polls")
    votes = db.get_list("votes")
    candidates = db.get_all("candidates")
    print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
    for pid in voted_polls:
        if pid in polls:
            poll = polls[pid]
            sc = GREEN if poll['status'] == 'open' else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
            for vr in [v for v in votes if v["poll_id"] == pid and v["voter_id"] == current_user["id"]]:
                pos_title = next((pos["position_title"] for pos in poll.get("positions", []) if pos["position_id"] == vr["position_id"]), "Unknown")
                if vr["abstained"]: print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else: print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
            print()
    pause()


def view_closed_poll_results_voter(db):
    clear_screen()
    header("ELECTION RESULTS", THEME_VOTER)
    polls = db.get_all("polls")
    votes = db.get_list("votes")
    candidates = db.get_all("candidates")
    closed = {pid: p for pid, p in polls.items() if p["status"] == "closed"}
    if not closed: print(); info("No closed polls with results."); pause(); return
    for pid, poll in closed.items():
        print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            vote_counts = {}; abstain_count = 0
            for v in votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    if v["abstained"]: abstain_count += 1
                    else: vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            total = sum(vote_counts.values()) + abstain_count
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
    pause()


def view_voter_profile(db, current_user):
    clear_screen()
    header("MY PROFILE", THEME_VOTER)
    v = current_user
    stations = db.get_all("voting_stations")
    station_name = stations.get(v["station_id"], {}).get("name", "Unknown")
    print()
    for label, value in [
        ("Name", v['full_name']), ("National ID", v['national_id']),
        ("Voter Card", f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
        ("Date of Birth", v['date_of_birth']), ("Age", v['age']), ("Gender", v['gender']),
        ("Address", v['address']), ("Phone", v['phone']), ("Email", v['email']),
        ("Station", station_name),
        ("Verified", status_badge('Yes', True) if v['is_verified'] else status_badge('No', False)),
        ("Registered", v['registered_at']), ("Polls Voted", len(v.get('has_voted_in', [])))
    ]:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
    pause()


def change_voter_password(db, current_user):
    clear_screen()
    header("CHANGE PASSWORD", THEME_VOTER)
    print()
    old_pass = masked_input("Current Password: ").strip()
    if hash_password(old_pass) != current_user["password"]: error("Incorrect current password."); pause(); return
    new_pass = masked_input("New Password: ").strip()
    if len(new_pass) < 6: error("Password must be at least 6 characters."); pause(); return
    confirm_pass = masked_input("Confirm New Password: ").strip()
    if new_pass != confirm_pass: error("Passwords do not match."); pause(); return
    current_user["password"] = hash_password(new_pass)
    voters = db.get_all("voters")
    for vid, v in voters.items():
        if v["id"] == current_user["id"]:
            db.update("voters", vid, {"password": hash_password(new_pass)}); break
    db.log_action("CHANGE_PASSWORD", current_user["voter_card_number"], "Password changed")
    print(); success("Password changed successfully!")
    pause()
