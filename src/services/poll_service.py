"""
Poll lifecycle: create, update, delete, open/close, assign candidates.
"""
import datetime

from src.config.constants import MIN_CANDIDATE_AGE
from src.data.repository import Repository


def create_poll(
    repo: Repository,
    current_username: str,
    title: str,
    description: str,
    election_type: str,
    start_date: str,
    end_date: str,
    position_ids: list,
    station_ids: list,
) -> tuple[bool, str]:
    """Create poll with positions and stations. Returns (success, message)."""
    if not title:
        return False, "Title cannot be empty."
    try:
        sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if ed <= sd:
            return False, "End date must be after start date."
    except ValueError:
        return False, "Invalid date format."
    active_positions = {pid: repo.positions[pid] for pid in repo.positions if repo.positions[pid]["is_active"]}
    poll_positions = []
    for spid in position_ids:
        if spid not in active_positions:
            continue
        p = repo.positions[spid]
        poll_positions.append({
            "position_id": spid,
            "position_title": p["title"],
            "candidate_ids": [],
            "max_winners": p["max_winners"],
        })
    if not poll_positions:
        return False, "No valid positions selected."
    if not station_ids:
        return False, "No voting stations selected."

    pid = repo.poll_id_counter
    repo.polls[pid] = {
        "id": pid,
        "title": title,
        "description": description,
        "election_type": election_type,
        "start_date": start_date,
        "end_date": end_date,
        "positions": poll_positions,
        "station_ids": station_ids,
        "status": "draft",
        "total_votes_cast": 0,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_username,
    }
    repo.poll_id_counter += 1
    return True, f"Poll '{title}' created! ID: {pid}"


def update_poll(
    repo: Repository,
    pid: int,
    current_username: str,
    title: str = None,
    description: str = None,
    election_type: str = None,
    start_date: str = None,
    end_date: str = None,
) -> tuple[bool, str]:
    """Update draft/closed poll (not open). Returns (success, message)."""
    if pid not in repo.polls:
        return False, "Poll not found."
    poll = repo.polls[pid]
    if poll["status"] == "open":
        return False, "Cannot update an open poll. Close it first."
    if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
        return False, "Cannot update a poll with votes."
    if title:
        poll["title"] = title
    if description is not None:
        poll["description"] = description
    if election_type:
        poll["election_type"] = election_type
    if start_date:
        try:
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            poll["start_date"] = start_date
        except ValueError:
            pass
    if end_date:
        try:
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            poll["end_date"] = end_date
        except ValueError:
            pass
    return True, "Poll updated!"


def delete_poll(repo: Repository, pid: int, current_username: str) -> tuple[bool, str]:
    """Delete poll and its votes. Fails if poll is open. Returns (success, message)."""
    if pid not in repo.polls:
        return False, "Poll not found."
    if repo.polls[pid]["status"] == "open":
        return False, "Cannot delete an open poll. Close it first."
    title = repo.polls[pid]["title"]
    del repo.polls[pid]
    repo.votes = [v for v in repo.votes if v["poll_id"] != pid]
    return True, f"Poll '{title}' deleted."


def open_poll(repo: Repository, pid: int, current_username: str) -> tuple[bool, str]:
    """Set poll status to open if draft and has candidates. Returns (success, message)."""
    if pid not in repo.polls:
        return False, "Poll not found."
    poll = repo.polls[pid]
    if poll["status"] != "draft":
        return False, "Only draft polls can be opened."
    if not any(pos["candidate_ids"] for pos in poll["positions"]):
        return False, "Cannot open - no candidates assigned."
    poll["status"] = "open"
    return True, f"Poll '{poll['title']}' is now OPEN for voting!"


def close_poll(repo: Repository, pid: int, current_username: str) -> tuple[bool, str]:
    """Set poll status to closed. Returns (success, message)."""
    if pid not in repo.polls:
        return False, "Poll not found."
    poll = repo.polls[pid]
    if poll["status"] != "open":
        return False, "Only open polls can be closed."
    poll["status"] = "closed"
    return True, f"Poll '{poll['title']}' is now CLOSED."


def reopen_poll(repo: Repository, pid: int, current_username: str) -> tuple[bool, str]:
    """Set closed poll back to open. Returns (success, message)."""
    if pid not in repo.polls:
        return False, "Poll not found."
    poll = repo.polls[pid]
    if poll["status"] != "closed":
        return False, "Only closed polls can be reopened."
    poll["status"] = "open"
    return True, "Poll reopened!"


def assign_candidates_to_poll(
    repo: Repository,
    pid: int,
    current_username: str,
    position_index: int,
    candidate_ids: list,
) -> tuple[bool, str]:
    """
    Set candidate_ids for a position in the poll. Only for draft/closed polls.
    candidate_ids must be eligible (active, approved, age >= position min).
    Returns (success, message).
    """
    if pid not in repo.polls:
        return False, "Poll not found."
    poll = repo.polls[pid]
    if poll["status"] == "open":
        return False, "Cannot modify candidates of an open poll."
    if position_index < 0 or position_index >= len(poll["positions"]):
        return False, "Invalid position index."
    pos = poll["positions"][position_index]
    pos_data = repo.positions.get(pos["position_id"], {})
    min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
    active = {cid: c for cid, c in repo.candidates.items() if c["is_active"] and c.get("is_approved", True)}
    eligible = {cid: c for cid, c in active.items() if c["age"] >= min_age}
    valid_ids = [cid for cid in candidate_ids if cid in eligible]
    pos["candidate_ids"] = valid_ids
    return True, f"{len(valid_ids)} candidate(s) assigned."
