"""
Voter actions: cast vote (with duplicate prevention), view history, change password.
"""
import datetime
import hashlib

from src.data.repository import Repository
from src.services.auth_service import AuthService


def get_open_polls_for_voter(repo: Repository, station_id: int) -> dict:
    """Return {poll_id: poll_dict} for open polls that include this station."""
    return {
        pid: p for pid, p in repo.polls.items()
        if p["status"] == "open" and station_id in p["station_ids"]
    }


def has_voted_in_poll(repo: Repository, voter_id: int, poll_id: int) -> bool:
    """Return True if voter has already voted in this poll."""
    return any(v["poll_id"] == poll_id and v["voter_id"] == voter_id for v in repo.votes)


def cast_vote(
    repo: Repository,
    voter: dict,
    poll_id: int,
    choices: list,
) -> tuple[bool, str, str]:
    """
    choices: list of dicts with position_id, position_title, candidate_id (or None), candidate_name, abstained.
    Returns (success, message, vote_hash_prefix).
    """
    if poll_id not in repo.polls:
        return False, "Poll not found.", ""
    poll = repo.polls[poll_id]
    if poll["status"] != "open":
        return False, "Poll is not open for voting.", ""
    if voter["station_id"] not in poll["station_ids"]:
        return False, "Your station is not assigned to this poll.", ""
    if has_voted_in_poll(repo, voter["id"], poll_id):
        return False, "You have already voted in this poll.", ""

    vote_timestamp = str(datetime.datetime.now())
    vote_hash = hashlib.sha256(f"{voter['id']}{poll_id}{vote_timestamp}".encode()).hexdigest()[:16]

    for ch in choices:
        repo.votes.append({
            "vote_id": vote_hash + str(ch["position_id"]),
            "poll_id": poll_id,
            "position_id": ch["position_id"],
            "candidate_id": ch.get("candidate_id"),
            "voter_id": voter["id"],
            "station_id": voter["station_id"],
            "timestamp": vote_timestamp,
            "abstained": ch.get("abstained", False),
        })

    voter["has_voted_in"] = voter.get("has_voted_in", []) + [poll_id]
    for vid, v in repo.voters.items():
        if v["id"] == voter["id"]:
            v["has_voted_in"] = v.get("has_voted_in", []) + [poll_id]
            break
    poll["total_votes_cast"] = poll.get("total_votes_cast", 0) + 1
    return True, "Your vote has been recorded successfully!", vote_hash


def change_voter_password(
    repo: Repository,
    voter: dict,
    old_password: str,
    new_password: str,
) -> tuple[bool, str]:
    """Change password if old password matches. Returns (success, message)."""
    if AuthService.hash_password(old_password) != voter["password"]:
        return False, "Incorrect current password."
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."
    hashed = AuthService.hash_password(new_password)
    voter["password"] = hashed
    for vid, v in repo.voters.items():
        if v["id"] == voter["id"]:
            v["password"] = hashed
            break
    return True, "Password changed successfully!"
