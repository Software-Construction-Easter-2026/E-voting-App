"""
Voter management: verify, deactivate, search. Registration is in auth_service.
"""
from src.data.repository import Repository


def verify_voter(repo: Repository, vid: int, current_username: str) -> tuple[bool, str]:
    """Mark voter as verified. Returns (success, message)."""
    if vid not in repo.voters:
        return False, "Voter not found."
    if repo.voters[vid]["is_verified"]:
        return False, "Already verified."
    repo.voters[vid]["is_verified"] = True
    return True, f"Voter '{repo.voters[vid]['full_name']}' verified!"


def verify_all_pending(repo: Repository, current_username: str) -> tuple[bool, str, int]:
    """Verify all unverified voters. Returns (success, message, count)."""
    unverified = [vid for vid, v in repo.voters.items() if not v["is_verified"]]
    for vid in unverified:
        repo.voters[vid]["is_verified"] = True
    return True, f"{len(unverified)} voters verified!", len(unverified)


def deactivate_voter(repo: Repository, vid: int, current_username: str) -> tuple[bool, str]:
    """Deactivate voter. Returns (success, message)."""
    if vid not in repo.voters:
        return False, "Voter not found."
    if not repo.voters[vid]["is_active"]:
        return False, "Already deactivated."
    repo.voters[vid]["is_active"] = False
    return True, "Voter deactivated."


def search_voters_by_name(repo: Repository, term: str) -> list:
    """Return list of voter dicts matching name."""
    return [v for v in repo.voters.values() if term in v["full_name"].lower()]


def search_voters_by_card(repo: Repository, card: str) -> list:
    """Return list of voter dicts matching card number (exact)."""
    return [v for v in repo.voters.values() if v["voter_card_number"] == card]


def search_voters_by_national_id(repo: Repository, nid: str) -> list:
    """Return list of voter dicts matching national ID."""
    return [v for v in repo.voters.values() if v["national_id"] == nid]


def search_voters_by_station(repo: Repository, station_id: int) -> list:
    """Return list of voter dicts at station."""
    return [v for v in repo.voters.values() if v["station_id"] == station_id]
