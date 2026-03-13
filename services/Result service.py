# Handles poll results, detailed statistics, station-wise results and audit log.

import storage.state as state
from utils.logger import audit_logger


def get_poll_results(poll_id: int) -> dict:
    #Calculate and return results for a given poll.
    if poll_id not in state.polls:
        return None

    poll = state.polls[poll_id]

    # Calculate voter turnout
    total_eligible = sum(
        1 for voter in state.voters.values()
        if voter["is_verified"] and voter["is_active"]
        and voter["station_id"] in poll["station_ids"]
    )
    turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0

    # Build results per position
    position_results = []

    for position in poll["positions"]:
        vote_counts   = {}
        abstain_count = 0
        total_pos     = 0

        for vote in state.votes:
            if vote["poll_id"] == poll_id and vote["position_id"] == position["position_id"]:
                total_pos += 1
                if vote["abstained"]:
                    abstain_count += 1
                else:
                    candidate_id = vote["candidate_id"]
                    vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1

        # Sort candidates by votes descending
        sorted_candidates = sorted(
            vote_counts.items(), key=lambda item: item[1], reverse=True
        )

        position_results.append({
            "position_id":        position["position_id"],
            "position_title":     position["position_title"],
            "max_winners":        position["max_winners"],
            "total_votes":        total_pos,
            "abstain_count":      abstain_count,
            "sorted_candidates":  sorted_candidates,
        })

    return {
        "poll":             poll,
        "total_eligible":   total_eligible,
        "turnout":          turnout,
        "position_results": position_results,
    }


def get_station_wise_results(poll_id: int) -> dict:
    #Return voting results broken down by station for a given poll.
   
    if poll_id not in state.polls:
        return None

    poll = state.polls[poll_id]
    station_results = []

    for station_id in poll["station_ids"]:
        if station_id not in state.voting_stations:
            continue

        station       = state.voting_stations[station_id]
        station_votes = [vote for vote in state.votes if vote["poll_id"] == poll_id and vote["station_id"] == station_id]

        # Count unique voters who voted at this station
        voters_who_voted = len(set(vote["voter_id"] for vote in station_votes))

        # Count registered voters at this station
        registered_at_station = sum(
            1 for voter in state.voters.values()
            if voter["station_id"] == station_id and voter["is_verified"] and voter["is_active"]
        )

        station_turnout = (
            voters_who_voted / registered_at_station * 100
        ) if registered_at_station > 0 else 0

        # Build per-position vote counts for this station
        position_breakdowns = []
        for position in poll["positions"]:
            position_votes = [vote for vote in station_votes if vote["position_id"] == position["position_id"]]
            vote_counts    = {}
            abstain_count  = 0

            for vote in position_votes:
                if vote["abstained"]:
                    abstain_count += 1
                else:
                    candidate_id = vote["candidate_id"]
                    vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1

            total = sum(vote_counts.values()) + abstain_count

            position_breakdowns.append({
                "position_title": position["position_title"],
                "vote_counts":    vote_counts,
                "abstain_count":  abstain_count,
                "total":          total,
            })

        station_results.append({
            "station":              station,
            "voters_who_voted":     voters_who_voted,
            "registered_at_station": registered_at_station,
            "station_turnout":      station_turnout,
            "position_breakdowns":  position_breakdowns,
        })

    return {
        "poll":            poll,
        "station_results": station_results,
    }


def get_detailed_statistics() -> dict:
    #Return a full system statistics summary.

    # Candidate counts
    total_candidates  = len(state.candidates)
    active_candidates = sum(1 for candidate in state.candidates.values() if candidate["is_active"])

    # Voter counts
    total_voters    = len(state.voters)
    verified_voters = sum(1 for voter in state.voters.values() if voter["is_verified"])
    active_voters   = sum(1 for voter in state.voters.values() if voter["is_active"])

    # Station counts
    total_stations  = len(state.voting_stations)
    active_stations = sum(1 for station in state.voting_stations.values() if station["is_active"])

    # Poll counts
    total_polls  = len(state.polls)
    open_polls   = sum(1 for poll in state.polls.values() if poll["status"] == "open")
    closed_polls = sum(1 for poll in state.polls.values() if poll["status"] == "closed")
    draft_polls  = sum(1 for poll in state.polls.values() if poll["status"] == "draft")

    # Voter age group distribution
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    gender_counts = {}

    for voter in state.voters.values():
        # Gender
        gender = voter.get("gender", "?")
        gender_counts[gender] = gender_counts.get(gender, 0) + 1

        # Age groups
        age = voter.get("age", 0)
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

    # Station load (registered voters vs capacity)
    station_loads = []
    for station_id, station in state.voting_stations.items():
        voter_count = sum(1 for voter in state.voters.values() if voter["station_id"] == station_id)
        load_percent = (voter_count / station["capacity"] * 100) if station["capacity"] > 0 else 0
        station_loads.append({
            "name":         station["name"],
            "voter_count":  voter_count,
            "capacity":     station["capacity"],
            "load_percent": load_percent,
        })

    # Party distribution among active candidates
    party_counts = {}
    for candidate in state.candidates.values():
        if candidate["is_active"]:
            party = candidate["party"]
            party_counts[party] = party_counts.get(party, 0) + 1

    # Education level distribution among active candidates
    education_counts = {}
    for candidate in state.candidates.values():
        if candidate["is_active"]:
            edu = candidate["education"]
            education_counts[edu] = education_counts.get(edu, 0) + 1

    return {
        "candidates":       {"total": total_candidates, "active": active_candidates},
        "voters":           {"total": total_voters, "verified": verified_voters, "active": active_voters},
        "stations":         {"total": total_stations, "active": active_stations},
        "polls":            {"total": total_polls, "open": open_polls, "closed": closed_polls, "draft": draft_polls},
        "total_votes":      len(state.votes),
        "gender_counts":    gender_counts,
        "age_groups":       age_groups,
        "station_loads":    station_loads,
        "party_counts":     party_counts,
        "education_counts": education_counts,
    }


def get_audit_log() -> list:
    return audit_logger.get_log()


def filter_audit_log(filter_by: str, filter_term: str) -> list:
    #Filter the audit log by action type or username.
    full_log = audit_logger.get_log()

    if filter_by == "action":
        return [entry for entry in full_log if entry["action"] == filter_term]

    elif filter_by == "user":
        return [entry for entry in full_log if filter_term.lower() in entry["user"].lower()]

    return full_log