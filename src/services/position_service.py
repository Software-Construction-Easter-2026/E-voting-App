"""
Position CRUD. Positions define roles in an election (e.g. President, Governor).
"""
import datetime

from src.config.constants import MIN_CANDIDATE_AGE
from src.data.repository import Repository


def create_position(
    repo: Repository,
    current_username: str,
    title: str,
    description: str,
    level: str,
    max_winners: int,
    min_candidate_age: int = None,
) -> tuple[bool, str]:
    """Create position. Level must be National/Regional/Local. Returns (success, message)."""
    if not title:
        return False, "Title cannot be empty."
    if level.lower() not in ("national", "regional", "local"):
        return False, "Invalid level."
    if max_winners <= 0:
        return False, "Must be at least 1."
    min_age = min_candidate_age if min_candidate_age is not None else MIN_CANDIDATE_AGE
    pid = repo.position_id_counter
    repo.positions[pid] = {
        "id": pid,
        "title": title,
        "description": description,
        "level": level.capitalize(),
        "max_winners": max_winners,
        "min_candidate_age": min_age,
        "is_active": True,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_username,
    }
    repo.position_id_counter += 1
    return True, f"Position '{title}' created! ID: {pid}"


def update_position(
    repo: Repository,
    pid: int,
    title: str = None,
    description: str = None,
    level: str = None,
    max_winners: int = None,
) -> tuple[bool, str]:
    """Update position. None means keep current."""
    if pid not in repo.positions:
        return False, "Position not found."
    p = repo.positions[pid]
    if title:
        p["title"] = title
    if description is not None:
        p["description"] = description
    if level and level.lower() in ("national", "regional", "local"):
        p["level"] = level.capitalize()
    if max_winners is not None:
        p["max_winners"] = max_winners
    return True, "Position updated!"


def delete_position(repo: Repository, pid: int, current_username: str) -> tuple[bool, str]:
    """Deactivate position if not in an open poll. Returns (success, message)."""
    if pid not in repo.positions:
        return False, "Position not found."
    for poll_id, poll in repo.polls.items():
        for pp in poll.get("positions", []):
            if pp["position_id"] == pid and poll["status"] == "open":
                return False, f"Cannot delete - in active poll: {poll['title']}"
    repo.positions[pid]["is_active"] = False
    return True, "Position deactivated."
