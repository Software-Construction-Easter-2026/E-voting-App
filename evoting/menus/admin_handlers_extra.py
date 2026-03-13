from evoting.core.colors import (
    BOLD,
    BRIGHT_WHITE,
    DIM,
    GRAY,
    GREEN,
    RED,
    RESET,
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    YELLOW,
)
from evoting.core.colors import BG_GREEN, BLACK
from evoting.core.constants import MIN_CANDIDATE_AGE
from evoting.ui import console_io, display


def assign_candidates_to_poll(ctx):
    repo, auth, poll_svc, candidate_svc, position_svc = (
        ctx.repo,
        ctx.auth,
        ctx.poll_svc,
        ctx.candidate_svc,
        ctx.position_svc,
    )
    polls = poll_svc.get_all()
    candidates = candidate_svc.get_all()
    positions = position_svc.get_all()
    console_io.clear_screen()
    display.header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    if not candidates:
        display.info("No candidates found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
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
    if poll["status"] == "open":
        display.error("Cannot modify candidates of an open poll.")
        console_io.pause()
        return
    position_candidate_ids = {}
    for pos in poll["positions"]:
        display.subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
        current_cands = [
            f"{ccid}: {candidates[ccid]['full_name']}"
            for ccid in pos["candidate_ids"]
            if ccid in candidates
        ]
        if current_cands:
            print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
        else:
            display.info("No candidates assigned yet.")
        active_candidates = {
            cid: c
            for cid, c in candidates.items()
            if c.get("is_active") and c.get("is_approved", True)
        }
        pos_data = positions.get(pos["position_id"], {})
        min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
        if not eligible:
            display.info("No eligible candidates found.")
            continue
        display.subheader("Available Candidates", THEME_ADMIN)
        for cid, c in eligible.items():
            marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
            print(
                f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}"
            )
        if console_io.prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
            try:
                new_cand_ids = [
                    int(x.strip())
                    for x in console_io.prompt("Enter Candidate IDs (comma-separated): ").split(",")
                ]
                valid_ids = [ncid for ncid in new_cand_ids if ncid in eligible]
                for ncid in new_cand_ids:
                    if ncid not in eligible:
                        display.warning(f"Candidate {ncid} not eligible. Skipping.")
                position_candidate_ids[pos["position_id"]] = valid_ids
                display.success(f"{len(valid_ids)} candidate(s) assigned.")
            except ValueError:
                display.error("Invalid input. Skipping this position.")
        else:
            position_candidate_ids[pos["position_id"]] = pos.get("candidate_ids", [])
    if position_candidate_ids:
        poll_svc.assign_candidates(pid, auth.current_user["username"], position_candidate_ids)
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_all_voters(ctx):
    voter_svc = ctx.voter_svc
    voters = voter_svc.get_all()
    console_io.clear_screen()
    display.header("ALL REGISTERED VOTERS", THEME_ADMIN)
    if not voters:
        print()
        display.info("No voters registered.")
        console_io.pause()
        return
    print()
    display.table_header(
        f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
        THEME_ADMIN,
    )
    display.table_divider(70, THEME_ADMIN)
    for vid, v in voters.items():
        verified = display.status_badge("Yes", True) if v.get("is_verified") else display.status_badge("No", False)
        active = display.status_badge("Yes", True) if v.get("is_active") else display.status_badge("No", False)
        print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
    verified_count = sum(1 for v in voters.values() if v.get("is_verified"))
    unverified_count = sum(1 for v in voters.values() if not v.get("is_verified"))
    print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
    console_io.pause()


def verify_voter(ctx):
    repo, auth, voter_svc = ctx.repo, ctx.auth, ctx.voter_svc
    unverified = voter_svc.get_unverified()
    console_io.clear_screen()
    display.header("VERIFY VOTER", THEME_ADMIN)
    if not unverified:
        print()
        display.info("No unverified voters.")
        console_io.pause()
        return
    display.subheader("Unverified Voters", THEME_ADMIN_ACCENT)
    for vid, v in unverified.items():
        print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
    print()
    display.menu_item(1, "Verify a single voter", THEME_ADMIN)
    display.menu_item(2, "Verify all pending voters", THEME_ADMIN)
    choice = console_io.prompt("\nChoice: ")
    if choice == "1":
        try:
            vid = int(console_io.prompt("Enter Voter ID: "))
        except ValueError:
            display.error("Invalid input.")
            console_io.pause()
            return
        if vid not in repo.voters:
            display.error("Voter not found.")
            console_io.pause()
            return
        if repo.voters[vid].get("is_verified"):
            display.info("Already verified.")
            console_io.pause()
            return
        voter_svc.verify(vid, auth.current_user["username"])
        print()
        display.success(f"Voter '{repo.voters[vid]['full_name']}' verified!")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    elif choice == "2":
        count = voter_svc.verify_all_pending(auth.current_user["username"])
        print()
        display.success(f"{count} voters verified!")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    console_io.pause()


def deactivate_voter(ctx):
    repo, auth, voter_svc = ctx.repo, ctx.auth, ctx.voter_svc
    console_io.clear_screen()
    display.header("DEACTIVATE VOTER", THEME_ADMIN)
    print()
    try:
        vid = int(console_io.prompt("Enter Voter ID to deactivate: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if vid not in repo.voters:
        display.error("Voter not found.")
        console_io.pause()
        return
    if not repo.voters[vid].get("is_active"):
        display.info("Already deactivated.")
        console_io.pause()
        return
    if console_io.prompt(f"Deactivate '{repo.voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
        voter_svc.deactivate(vid, auth.current_user["username"])
        print()
        display.success("Voter deactivated.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    console_io.pause()


def search_voters(ctx):
    voter_svc = ctx.voter_svc
    console_io.clear_screen()
    display.header("SEARCH VOTERS", THEME_ADMIN)
    display.subheader("Search by", THEME_ADMIN_ACCENT)
    display.menu_item(1, "Name", THEME_ADMIN)
    display.menu_item(2, "Voter Card Number", THEME_ADMIN)
    display.menu_item(3, "National ID", THEME_ADMIN)
    display.menu_item(4, "Station", THEME_ADMIN)
    choice = console_io.prompt("\nChoice: ")
    results = []
    if choice == "1":
        term = console_io.prompt("Name: ")
        results = voter_svc.search_by_name(term)
    elif choice == "2":
        term = console_io.prompt("Card Number: ")
        results = voter_svc.search_by_card(term)
    elif choice == "3":
        term = console_io.prompt("National ID: ")
        results = voter_svc.search_by_national_id(term)
    elif choice == "4":
        try:
            sid = int(console_io.prompt("Station ID: "))
            results = voter_svc.search_by_station(sid)
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
        display.info("No voters found.")
    else:
        print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
        for v in results:
            verified = display.status_badge("Verified", True) if v.get("is_verified") else display.status_badge("Unverified", False)
            print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
    console_io.pause()


def create_admin(ctx):
    repo, auth, admin_svc = ctx.repo, ctx.auth, ctx.admin_svc
    console_io.clear_screen()
    display.header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
    if auth.current_user.get("role") != "super_admin":
        print()
        display.error("Only super admins can create admin accounts.")
        console_io.pause()
        return
    print()
    username = console_io.prompt("Username: ")
    if not username:
        display.error("Username cannot be empty.")
        console_io.pause()
        return
    full_name = console_io.prompt("Full Name: ")
    email = console_io.prompt("Email: ")
    password = console_io.masked_input("Password: ").strip()
    display.subheader("Available Roles", THEME_ADMIN_ACCENT)
    display.menu_item(1, f"super_admin {DIM}─ Full access{RESET}", THEME_ADMIN)
    display.menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}", THEME_ADMIN)
    display.menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
    display.menu_item(4, f"auditor {DIM}─ Read-only access{RESET}", THEME_ADMIN)
    role_choice = console_io.prompt("\nSelect role (1-4): ")
    data = {
        "username": username,
        "full_name": full_name,
        "email": email or "",
        "password": password,
        "role_choice": role_choice,
    }
    ok, result = admin_svc.create(auth.current_user["username"], data)
    if not ok:
        if result == "forbidden":
            display.error("Only super admins can create admin accounts.")
        elif result == "duplicate_username":
            display.error("Username already exists.")
        elif result == "short_password":
            display.error("Password must be at least 6 characters.")
        elif result == "invalid_role":
            display.error("Invalid role.")
        console_io.pause()
        return
    print()
    display.success(f"Admin '{result[0]}' created with role: {result[1]}")
    try:
        repo.save()
        display.info("Data saved successfully")
    except Exception as e:
        display.error(f"Error saving data: {e}")
    console_io.pause()


def view_admins(ctx):
    admin_svc = ctx.admin_svc
    admins = admin_svc.get_all()
    console_io.clear_screen()
    display.header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    print()
    display.table_header(
        f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
        THEME_ADMIN,
    )
    display.table_divider(78, THEME_ADMIN)
    for aid, a in admins.items():
        active = display.status_badge("Yes", True) if a.get("is_active") else display.status_badge("No", False)
        print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    console_io.pause()


def deactivate_admin(ctx):
    repo, auth, admin_svc = ctx.repo, ctx.auth, ctx.admin_svc
    admins = admin_svc.get_all()
    console_io.clear_screen()
    display.header("DEACTIVATE ADMIN", THEME_ADMIN)
    if auth.current_user.get("role") != "super_admin":
        print()
        display.error("Only super admins can deactivate admins.")
        console_io.pause()
        return
    print()
    for aid, a in admins.items():
        active = display.status_badge("Active", True) if a.get("is_active") else display.status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
    try:
        aid = int(console_io.prompt("\nEnter Admin ID to deactivate: "))
    except ValueError:
        display.error("Invalid input.")
        console_io.pause()
        return
    if aid not in admins:
        display.error("Admin not found.")
        console_io.pause()
        return
    if aid == auth.current_user["id"]:
        display.error("Cannot deactivate your own account.")
        console_io.pause()
        return
    if console_io.prompt(f"Deactivate '{admins[aid]['username']}'? (yes/no): ").lower() == "yes":
        ok, result = admin_svc.deactivate(aid, auth.current_user["username"], auth.current_user["id"])
        if not ok:
            if result == "forbidden":
                display.error("Only super admins can deactivate admins.")
            elif result == "self":
                display.error("Cannot deactivate your own account.")
            console_io.pause()
            return
        print()
        display.success("Admin deactivated.")
        try:
            repo.save()
            display.info("Data saved successfully")
        except Exception as e:
            display.error(f"Error saving data: {e}")
    console_io.pause()


def view_poll_results(ctx):
    repo, results_svc, candidate_svc = ctx.repo, ctx.results_svc, ctx.candidate_svc
    polls = repo.polls
    console_io.clear_screen()
    display.header("POLL RESULTS", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
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
    result = results_svc.get_poll_results(pid)
    if not result:
        console_io.pause()
        return
    poll = result["poll"]
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header(f"RESULTS: {poll['title']}", THEME_ADMIN)
    sc = GREEN if poll["status"] == "open" else RED
    print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
    total_eligible = results_svc.get_eligible_voters_count(pid)
    turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0
    tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
    print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
    for item in result["positions"]:
        pos = item["position"]
        display.subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
        vote_counts = item["vote_counts"]
        abstain_count = item["abstain_count"]
        total_pos = item["total"]
        for rank, (cid, count) in enumerate(item["sorted_candidates"], 1):
            cand = candidates.get(cid, {})
            pct = (count / total_pos * 100) if total_pos > 0 else 0
            bl = int(pct / 2)
            bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
            winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
            print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
            print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
        if abstain_count > 0:
            print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
        if not vote_counts:
            display.info("    No votes recorded for this position.")
    console_io.pause()


def view_detailed_statistics(ctx):
    from evoting.core.colors import RESET
    results_svc = ctx.results_svc
    stats = results_svc.get_detailed_statistics()
    console_io.clear_screen()
    display.header("DETAILED STATISTICS", THEME_ADMIN)
    display.subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
    o = stats["overview"]
    print(f"  {THEME_ADMIN}Candidates:{RESET}  {o['total_candidates']} {DIM}(Active: {o['active_candidates']}){RESET}")
    print(f"  {THEME_ADMIN}Voters:{RESET}      {o['total_voters']} {DIM}(Verified: {o['verified_voters']}, Active: {o['active_voters']}){RESET}")
    print(f"  {THEME_ADMIN}Stations:{RESET}    {o['total_stations']} {DIM}(Active: {o['active_stations']}){RESET}")
    print(f"  {THEME_ADMIN}Polls:{RESET}       {o['total_polls']} {DIM}({GREEN}Open: {o['open_polls']}{RESET}{DIM}, {RED}Closed: {o['closed_polls']}{RESET}{DIM}, {YELLOW}Draft: {o['draft_polls']}{RESET}{DIM}){RESET}")
    print(f"  {THEME_ADMIN}Total Votes:{RESET} {o['total_votes']}")
    display.subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
    tv = stats["total_voters_for_pct"]
    for g, count in stats["gender_counts"].items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {g}: {count} ({pct:.1f}%)")
    print(f"  {BOLD}Age Distribution:{RESET}")
    for group, count in stats["age_groups"].items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
    display.subheader("STATION LOAD", THEME_ADMIN_ACCENT)
    for sl in stats["station_load"]:
        s = sl["station"]
        vc = sl["voter_count"]
        cap = sl["capacity"]
        lp = sl["load_pct"]
        lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
        st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
        print(f"    {s['name']}: {vc}/{cap} {lc}({lp:.0f}%){RESET} {st}")
    display.subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
    for party, count in sorted(stats["party_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
    display.subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
    for edu, count in stats["edu_counts"].items():
        print(f"    {edu}: {BOLD}{count}{RESET}")
    console_io.pause()


def station_wise_results(ctx):
    repo, results_svc, candidate_svc = ctx.repo, ctx.results_svc, ctx.candidate_svc
    polls = repo.polls
    candidates = candidate_svc.get_all()
    console_io.clear_screen()
    display.header("STATION-WISE RESULTS", THEME_ADMIN)
    if not polls:
        display.info("No polls found.")
        console_io.pause()
        return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
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
    result = results_svc.get_station_wise_results(pid)
    if not result:
        console_io.pause()
        return
    console_io.clear_screen()
    display.header(f"STATION RESULTS: {result['poll']['title']}", THEME_ADMIN)
    for sd in result["stations_data"]:
        station = sd["station"]
        display.subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
        tc = GREEN if sd["turnout_pct"] > 50 else (YELLOW if sd["turnout_pct"] > 25 else RED)
        print(f"  {DIM}Registered:{RESET} {sd['registered']}  {DIM}│  Voted:{RESET} {sd['unique_voters']}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{sd['turnout_pct']:.1f}%{RESET}")
        for pr in sd["position_results"]:
            print(f"    {THEME_ADMIN_ACCENT}▸ {pr['position']['position_title']}:{RESET}")
            vc = pr["counts"]
            ac = pr["abstain_count"]
            total = pr["total"]
            for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
            if ac > 0:
                print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
    console_io.pause()


def view_audit_log(ctx):
    repo = ctx.repo
    console_io.clear_screen()
    display.header("AUDIT LOG", THEME_ADMIN)
    if not repo.audit_log:
        display.info("No audit records.")
        console_io.pause()
        return
    print(f"\n  {DIM}Total Records: {len(repo.audit_log)}{RESET}")
    display.subheader("Filter", THEME_ADMIN_ACCENT)
    display.menu_item(1, "Last 20 entries", THEME_ADMIN)
    display.menu_item(2, "All entries", THEME_ADMIN)
    display.menu_item(3, "Filter by action type", THEME_ADMIN)
    display.menu_item(4, "Filter by user", THEME_ADMIN)
    choice = console_io.prompt("\nChoice: ")
    entries = repo.audit_log
    if choice == "1":
        entries = repo.audit_log[-20:]
    elif choice == "3":
        action_types = list(set(e["action"] for e in repo.audit_log))
        for i, at in enumerate(action_types, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
        try:
            at_choice = int(console_io.prompt("Select action type: "))
            entries = [e for e in repo.audit_log if e["action"] == action_types[at_choice - 1]]
        except (ValueError, IndexError):
            display.error("Invalid choice.")
            console_io.pause()
            return
    elif choice == "4":
        uf = console_io.prompt("Enter username/card number: ")
        entries = [e for e in repo.audit_log if uf.lower() in e["user"].lower()]
    print()
    display.table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
    display.table_divider(100, THEME_ADMIN)
    for entry in entries:
        ac = (
            GREEN
            if "CREATE" in entry["action"] or entry["action"] == "LOGIN"
            else (
                RED
                if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]
                else (YELLOW if "UPDATE" in entry["action"] else RESET)
            )
        )
        print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET} {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
    console_io.pause()
