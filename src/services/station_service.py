"""
Voting station CRUD. No business rules beyond validation.
"""
import datetime

from src.data.repository import Repository


def create_station(
    repo: Repository,
    current_username: str,
    name: str,
    location: str,
    region: str,
    capacity: int,
    supervisor: str,
    contact: str,
    opening_time: str,
    closing_time: str,
) -> tuple[bool, str]:
    """Create voting station. Returns (success, message)."""
    if not name:
        return False, "Name cannot be empty."
    if not location:
        return False, "Location cannot be empty."
    if capacity <= 0:
        return False, "Capacity must be positive."
    sid = repo.station_id_counter
    repo.voting_stations[sid] = {
        "id": sid,
        "name": name,
        "location": location,
        "region": region,
        "capacity": capacity,
        "registered_voters": 0,
        "supervisor": supervisor,
        "contact": contact,
        "opening_time": opening_time,
        "closing_time": closing_time,
        "is_active": True,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_username,
    }
    repo.station_id_counter += 1
    return True, f"Voting Station '{name}' created! ID: {sid}"


def update_station(
    repo: Repository,
    sid: int,
    name: str = None,
    location: str = None,
    region: str = None,
    capacity: int = None,
    supervisor: str = None,
    contact: str = None,
) -> tuple[bool, str]:
    """Update station. None means keep current."""
    if sid not in repo.voting_stations:
        return False, "Station not found."
    s = repo.voting_stations[sid]
    if name:
        s["name"] = name
    if location is not None:
        s["location"] = location
    if region is not None:
        s["region"] = region
    if capacity is not None:
        s["capacity"] = capacity
    if supervisor is not None:
        s["supervisor"] = supervisor
    if contact is not None:
        s["contact"] = contact
    return True, f"Station '{s['name']}' updated successfully!"


def delete_station(repo: Repository, sid: int, current_username: str) -> tuple[bool, str]:
    """Deactivate station. Returns (success, message)."""
    if sid not in repo.voting_stations:
        return False, "Station not found."
    name = repo.voting_stations[sid]["name"]
    repo.voting_stations[sid]["is_active"] = False
    return True, f"Station '{name}' deactivated."


def count_registered_at_station(repo: Repository, sid: int) -> int:
    """Return number of voters registered at this station."""
    return sum(1 for v in repo.voters.values() if v["station_id"] == sid)
