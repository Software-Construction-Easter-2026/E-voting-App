"""
stats_results.py - Admin-facing stats and results matching the original app.
All data access through DatabaseEngine.
"""
from ui import (clear_screen, header, subheader, menu_item, prompt,
                pause, error, success, warning, info,
                table_header, table_divider)
from colors import *


def view_poll_results(db):
    clear_screen()
    header("POLL RESULTS", THEME_ADMIN)
    polls = db.get_all("polls")
    voters = db.get_all("voters")
    votes = db.get_list("votes")
    candidates = db.get_all("candidates")
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    print()
    header(f"RESULTS: {poll['title']}", THEME_ADMIN)
    sc = GREEN if poll['status'] == 'open' else RED
    print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
    total_eligible = sum(1 for v in voters.values() if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"])
    turnout = (poll['total_votes_cast'] / total_eligible * 100) if total_eligible > 0 else 0
    tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
    print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
    for pos in poll["positions"]:
        subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
        vote_counts = {}; abstain_count = 0; total_pos = 0
        for v in votes:
            if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                total_pos += 1
                if v["abstained"]: abstain_count += 1
                else: vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
            cand = candidates.get(cid, {})
            pct = (count / total_pos * 100) if total_pos > 0 else 0
            bl = int(pct / 2)
            bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
            winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
            print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
            print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
        if abstain_count > 0: print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
        if not vote_counts: info("    No votes recorded for this position.")
    pause()


def view_detailed_statistics(db):
    clear_screen()
    header("DETAILED STATISTICS", THEME_ADMIN)
    candidates = db.get_all("candidates")
    voters = db.get_all("voters")
    stations = db.get_all("voting_stations")
    polls = db.get_all("polls")
    votes = db.get_list("votes")
    subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
    tc_count = len(candidates); ac = sum(1 for c in candidates.values() if c["is_active"])
    tv = len(voters); vv = sum(1 for v in voters.values() if v["is_verified"])
    av = sum(1 for v in voters.values() if v["is_active"])
    ts = len(stations); ast = sum(1 for s in stations.values() if s["is_active"])
    tp = len(polls)
    op = sum(1 for p in polls.values() if p["status"] == "open")
    cp = sum(1 for p in polls.values() if p["status"] == "closed")
    dp = sum(1 for p in polls.values() if p["status"] == "draft")
    print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc_count} {DIM}(Active: {ac}){RESET}")
    print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
    print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
    print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
    print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(votes)}")
    subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
    gender_counts = {}
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    for v in voters.values():
        gender_counts[v.get("gender", "?")] = gender_counts.get(v.get("gender", "?"), 0) + 1
        age = v.get("age", 0)
        if age <= 25: age_groups["18-25"] += 1
        elif age <= 35: age_groups["26-35"] += 1
        elif age <= 45: age_groups["36-45"] += 1
        elif age <= 55: age_groups["46-55"] += 1
        elif age <= 65: age_groups["56-65"] += 1
        else: age_groups["65+"] += 1
    for g, count in gender_counts.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {g}: {count} ({pct:.1f}%)")
    print(f"  {BOLD}Age Distribution:{RESET}")
    for group, count in age_groups.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
    subheader("STATION LOAD", THEME_ADMIN_ACCENT)
    for sid, s in stations.items():
        vc = sum(1 for v in voters.values() if v["station_id"] == sid)
        lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
        lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
        st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
        print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
    subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
    party_counts = {}
    for c in candidates.values():
        if c["is_active"]: party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
    for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
    subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
    edu_counts = {}
    for c in candidates.values():
        if c["is_active"]: edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
    for edu, count in edu_counts.items():
        print(f"    {edu}: {BOLD}{count}{RESET}")
    pause()


def station_wise_results(db):
    clear_screen()
    header("STATION-WISE RESULTS", THEME_ADMIN)
    polls = db.get_all("polls")
    voters = db.get_all("voters")
    votes = db.get_list("votes")
    candidates = db.get_all("candidates")
    stations = db.get_all("voting_stations")
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    print()
    header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
    for sid in poll["station_ids"]:
        if sid not in stations: continue
        station = stations[sid]
        subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
        station_votes = [v for v in votes if v["poll_id"] == pid and v["station_id"] == sid]
        svc = len(set(v["voter_id"] for v in station_votes))
        ras = sum(1 for v in voters.values() if v["station_id"] == sid and v["is_verified"] and v["is_active"])
        st = (svc / ras * 100) if ras > 0 else 0
        tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
        print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
        for pos in poll["positions"]:
            print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
            pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
            vc = {}; ac_count = 0
            for v in pv:
                if v["abstained"]: ac_count += 1
                else: vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
            total = sum(vc.values()) + ac_count
            for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
            if ac_count > 0: print(f"      {GRAY}Abstained: {ac_count} ({(ac_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
    pause()


def view_audit_log(db):
    clear_screen()
    header("AUDIT LOG", THEME_ADMIN)
    audit_log = db.get_list("audit_log")
    if not audit_log: print(); info("No audit records."); pause(); return
    print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
    subheader("Filter", THEME_ADMIN_ACCENT)
    menu_item(1, "Last 20 entries", THEME_ADMIN); menu_item(2, "All entries", THEME_ADMIN)
    menu_item(3, "Filter by action type", THEME_ADMIN); menu_item(4, "Filter by user", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    entries = audit_log
    if choice == "1": entries = audit_log[-20:]
    elif choice == "3":
        action_types = list(set(e["action"] for e in audit_log))
        for i, at in enumerate(action_types, 1): print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
        try: at_choice = int(prompt("Select action type: ")); entries = [e for e in audit_log if e["action"] == action_types[at_choice - 1]]
        except (ValueError, IndexError): error("Invalid choice."); pause(); return
    elif choice == "4":
        uf = prompt("Enter username/card number: ")
        entries = [e for e in audit_log if uf.lower() in e["user"].lower()]
    print()
    table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
    table_divider(100, THEME_ADMIN)
    for entry in entries:
        ac = GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN" else (RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"] else (YELLOW if "UPDATE" in entry["action"] else RESET))
        print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET} {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
    pause()
