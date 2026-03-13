# Handles ballot casting, vote recording and voting history.

import hashlib
import storage.state as state
from utils.helpers import current_timestamp
from utils.logger import audit_logger
from storage.store import save_data


def get_available_polls_for_voter(voter: dict) -> dict:
    #Return polls the voter is eligible to vote in and excludes polls they have already voted in.
    available = {}

    for poll_id_key, poll in state.polls.items():
        already_voted   = poll_id_key in voter.get("has_voted_in", [])
        station_allowed = voter["station_id"] in poll["station_ids"]

        if poll["status"] == "open" and not already_voted and station_allowed:
            available[poll_id_key] = poll

    return available


def cast_vote(voter: dict, poll_id: int, vote_selections: list):
  
    if poll_id not in state.polls:
        return False, "Poll not found.", None

    poll = state.polls[poll_id]

    # Double-check the poll is still open
    if poll["status"] != "open":
        return False, "This poll is no longer open.", None

    # Double-check the voter has not already voted
    if poll_id in voter.get("has_voted_in", []):
        return False, "You have already voted in this poll.", None

    # Generate a unique vote reference hash
    vote_timestamp = current_timestamp()
    vote_hash = hashlib.sha256(
        f"{voter['id']}{poll_id}{vote_timestamp}".encode()
    ).hexdigest()[:16]

    # Record each position vote
    for selection in vote_selections:
        state.votes.append({
            "vote_id":     vote_hash + str(selection["position_id"]),
            "poll_id":     poll_id,
            "position_id": selection["position_id"],
            "candidate_id": selection.get("candidate_id"),
            "voter_id":    voter["id"],
            "station_id":  voter["station_id"],
            "timestamp":   vote_timestamp,
            "abstained":   selection.get("abstained", False),
        })

    # Mark voter as having voted in this poll
    voter["has_voted_in"].append(poll_id)

    # Update the voter record in state
    for voter_id, stored_voter in state.voters.items():
        if stored_voter["id"] == voter["id"]:
            stored_voter["has_voted_in"].append(poll_id)
            break

    # Increment total votes cast for the poll
    poll["total_votes_cast"] += 1

    audit_logger.log(
        "CAST_VOTE",
        voter["voter_card_number"],
        f"Voted in poll: {poll['title']} (Hash: {vote_hash})"
    )
    save_data()
    return True, "Your vote has been recorded successfully.", vote_hash


def get_voting_history(voter: dict) -> list:
    history = []
    voted_poll_ids = voter.get("has_voted_in", [])

    for poll_id_key in voted_poll_ids:
        if poll_id_key not in state.polls:
            continue

        poll = state.polls[poll_id_key]

        # Get the individual votes this voter cast in this poll
        voter_votes = [
            vote for vote in state.votes
            if vote["poll_id"] == poll_id_key and vote["voter_id"] == voter["id"]
        ]

        history.append({
            "poll_id":     poll_id_key,
            "poll_title":  poll["title"],
            "poll_status": poll["status"],
            "election_type": poll["election_type"],
            "votes":       voter_votes,
        })

    return history