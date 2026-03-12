
# Results and statistics: tally votes, turnout, demographics, station load.
# Read-only: returns data for the UI layer to display.

from src.data.repository import Repository


def get_poll_results(repo: Repository, poll_id: int) -> dict:
    """
    Return structure for displaying poll results: positions with vote counts per candidate,
    abstains, total eligible, turnout. Keys: poll, total_eligible, turnout_pct, positions_data.
    """
    if poll_id not in repo.polls:
        return None
    poll = repo.polls[poll_id]
    total_eligible = sum(
        1 for v in repo.voters.values()
        if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"]
    )
    turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0
    positions_data = []
    for pos in poll["positions"]:
        vote_counts = {}
        abstain_count = 0
        for v in repo.votes:
            if v["poll_id"] == poll_id and v["position_id"] == pos["position_id"]:
                if v["abstained"]:
                    abstain_count += 1
                else:
                    vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        total_pos = sum(vote_counts.values()) + abstain_count
        sorted_candidates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
        positions_data.append({
            "position": pos,
            "vote_counts": vote_counts,
            "abstain_count": abstain_count,
            "total": total_pos,
            "sorted_candidates": sorted_candidates,
        })
    return {
        "poll": poll,
        "total_eligible": total_eligible,
        "turnout_pct": turnout,
        "positions_data": positions_data,
    }


def get_detailed_statistics(repo: Repository) -> dict:
    """
    Return system overview, voter demographics, station load, party and education distribution.
    """
    tc = len(repo.candidates)
    ac = sum(1 for c in repo.candidates.values() if c["is_active"])
    tv = len(repo.voters)
    vv = sum(1 for v in repo.voters.values() if v["is_verified"])
    av = sum(1 for v in repo.voters.values() if v["is_active"])
    ts = len(repo.voting_stations)
    ast = sum(1 for s in repo.voting_stations.values() if s["is_active"])
    tp = len(repo.polls)
    op = sum(1 for p in repo.polls.values() if p["status"] == "open")
    cp = sum(1 for p in repo.polls.values() if p["status"] == "closed")
    dp = sum(1 for p in repo.polls.values() if p["status"] == "draft")

    gender_counts = {}
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    for v in repo.voters.values():
        g = v.get("gender", "?")
        gender_counts[g] = gender_counts.get(g, 0) + 1
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

    station_load = []
    for sid, s in repo.voting_stations.items():
        vc = sum(1 for v in repo.voters.values() if v["station_id"] == sid)
        lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
        station_load.append({"station": s, "registered": vc, "load_pct": lp})

    party_counts = {}
    for c in repo.candidates.values():
        if c["is_active"]:
            party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
    edu_counts = {}
    for c in repo.candidates.values():
        if c["is_active"]:
            edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1

    return {
        "candidates_total": tc,
        "candidates_active": ac,
        "voters_total": tv,
        "voters_verified": vv,
        "voters_active": av,
        "stations_total": ts,
        "stations_active": ast,
        "polls_total": tp,
        "polls_open": op,
        "polls_closed": cp,
        "polls_draft": dp,
        "total_votes_count": len(repo.votes),
        "gender_counts": gender_counts,
        "age_groups": age_groups,
        "station_load": station_load,
        "party_counts": party_counts,
        "edu_counts": edu_counts,
    }


def get_station_wise_results(repo: Repository, poll_id: int) -> dict:
    """Return per-station vote counts for a poll. Keys: poll, stations (list of station_id, station, positions_results)."""
    if poll_id not in repo.polls:
        return None
    poll = repo.polls[poll_id]
    result = {"poll": poll, "stations": []}
    for sid in poll["station_ids"]:
        if sid not in repo.voting_stations:
            continue
        station = repo.voting_stations[sid]
        station_votes = [v for v in repo.votes if v["poll_id"] == poll_id and v["station_id"] == sid]
        svc = len(set(v["voter_id"] for v in station_votes))
        ras = sum(1 for v in repo.voters.values() if v["station_id"] == sid and v["is_verified"] and v["is_active"])
        st = (svc / ras * 100) if ras > 0 else 0
        pos_results = []
        for pos in poll["positions"]:
            pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
            vc = {}
            ac = 0
            for v in pv:
                if v["abstained"]:
                    ac += 1
                else:
                    vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
            total = sum(vc.values()) + ac
            pos_results.append({
                "position": pos,
                "vote_counts": vc,
                "abstain_count": ac,
                "total": total,
            })
        result["stations"].append({
            "station_id": sid,
            "station": station,
            "voted_count": svc,
            "registered_count": ras,
            "turnout_pct": st,
            "positions_results": pos_results,
        })
    return result
