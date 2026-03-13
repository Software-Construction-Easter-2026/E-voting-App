"""
stations.py

Voting station management module.
One class per operation. Each class does exactly one thing.
Data is stored in data/stations.json.

A VotingStation is a physical location where voters cast their ballots.
Stations are referenced by polls and assigned to voters.

Classes:
    StationStore         — shared JsonStore instance for this module
    CreateStation        — validates and inserts a new voting station
    GetAllStations       — returns every station
    GetStation           — returns one station by id
    UpdateStation        — edits allowed fields on an existing station
    DeactivateStation    — marks a station inactive (warns if voters are registered there)
    CountRegisteredVoters — counts how many voters are assigned to a given station
"""

import datetime
from storage import JsonStore


# ── Shared store ──────────────────────────────────────────────────────────────

class StationStore:
    """Single access point to the stations JSON file for all station operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/stations.json")
        return cls._instance


# ── Invariants ────────────────────────────────────────────────────────────────

def _require_station_name_is_not_empty(name: str) -> None:
    if not name:
        raise ValueError("Station name cannot be empty.")


def _require_location_is_not_empty(location: str) -> None:
    if not location:
        raise ValueError("Station location cannot be empty.")


def _require_positive_capacity(capacity: int) -> None:
    if capacity <= 0:
        raise ValueError("Voter capacity must be a positive number.")


def _require_station_is_currently_active(station: dict) -> None:
    if not station["is_active"]:
        raise ValueError(f"Station '{station['name']}' is already inactive.")


# ── Operations ────────────────────────────────────────────────────────────────

class CreateStation:
    """Validates inputs and creates a new active voting station."""

    def __init__(self, created_by: str) -> None:
        self._station_store = StationStore.get()
        self._created_by    = created_by

    def execute(
        self,
        name:           str,
        location:       str,
        region:         str,
        capacity:       int,
        supervisor:     str,
        contact_phone:  str,
        opening_time:   str,
        closing_time:   str,
    ) -> dict:
        _require_station_name_is_not_empty(name)
        _require_location_is_not_empty(location)
        _require_positive_capacity(capacity)

        new_station = {
            "name":               name,
            "location":           location,
            "region":             region,
            "capacity":           capacity,
            "registered_voters":  0,
            "supervisor":         supervisor,
            "contact_phone":      contact_phone,
            "opening_time":       opening_time,
            "closing_time":       closing_time,
            "is_active":          True,
            "created_by":         self._created_by,
            "created_at":         str(datetime.datetime.now()),
        }
        return self._station_store.insert(new_station)


class GetAllStations:
    """Returns every voting station in the store."""

    def __init__(self) -> None:
        self._station_store = StationStore.get()

    def execute(self) -> list[dict]:
        return self._station_store.all()


class GetStation:
    """Returns a single station by id, or raises ValueError if not found."""

    def __init__(self) -> None:
        self._station_store = StationStore.get()

    def execute(self, station_id: int) -> dict:
        matching_station = self._station_store.find_one(id=station_id)
        if matching_station is None:
            raise ValueError(f"Station {station_id} not found.")
        return matching_station


class UpdateStation:
    """Edits allowed fields on an existing voting station."""

    EDITABLE_FIELDS = {
        "name", "location", "region",
        "capacity", "supervisor", "contact_phone",
    }

    def __init__(self) -> None:
        self._station_store = StationStore.get()

    def execute(self, station_id: int, requested_changes: dict) -> dict:
        GetStation().execute(station_id)   # confirms it exists

        if "name" in requested_changes:
            _require_station_name_is_not_empty(requested_changes["name"])

        if "location" in requested_changes:
            _require_location_is_not_empty(requested_changes["location"])

        if "capacity" in requested_changes:
            _require_positive_capacity(requested_changes["capacity"])

        # Strip out any fields that are not editable through this operation.
        safe_changes = {
            field_name: new_value
            for field_name, new_value in requested_changes.items()
            if field_name in self.EDITABLE_FIELDS and new_value not in (None, "")
        }

        return self._station_store.update(station_id, safe_changes)


class CountRegisteredVoters:
    """
    Counts how many voters from the given voter list are assigned to a station.
    Pass in the full list of voter records to count against.

    Usage:
        all_voters = GetAllVoters().execute()
        count = CountRegisteredVoters(all_voters).execute(station_id)
    """

    def __init__(self, all_voters: list[dict]) -> None:
        self._all_voters = all_voters

    def execute(self, station_id: int) -> int:
        return sum(
            1 for voter in self._all_voters
            if voter["station_id"] == station_id
        )


class DeactivateStation:
    """
    Marks a voting station as inactive.
    Raises ValueError if the station is already inactive.
    Raises ValueError if voters are still registered at the station,
    unless force=True is passed to override this check.
    """

    def __init__(self, all_voters: list[dict]) -> None:
        self._station_store = StationStore.get()
        self._all_voters    = all_voters

    def execute(self, station_id: int, force: bool = False) -> dict:
        station_to_deactivate  = GetStation().execute(station_id)
        _require_station_is_currently_active(station_to_deactivate)

        number_of_registered_voters = CountRegisteredVoters(self._all_voters).execute(station_id)
        if number_of_registered_voters > 0 and not force:
            raise ValueError(
                f"{number_of_registered_voters} voter(s) are still registered at "
                f"'{station_to_deactivate['name']}'. "
                f"Pass force=True to deactivate anyway."
            )

        return self._station_store.update(station_id, {"is_active": False})