"""
positions.py

Position management module.
One class per operation. Each class does exactly one thing.
Data is stored in data/positions.json.

A Position represents an elected seat (e.g. President, Governor, Senator).
Positions are referenced by polls — a poll holds one or more positions,
and candidates are assigned to those positions.

Classes:
    PositionStore    — shared JsonStore instance for this module
    CreatePosition   — validates and inserts a new position
    GetAllPositions  — returns every position
    GetPosition      — returns one position by id
    UpdatePosition   — edits a position that is not in an active poll
    DeactivatePosition — marks a position inactive (cannot delete if used in open poll)
"""

import datetime
from storage import JsonStore


# ── Shared store ──────────────────────────────────────────────────────────────

class PositionStore:
    """Single access point to the positions JSON file for all position operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/positions.json")
        return cls._instance


# ── Constants ─────────────────────────────────────────────────────────────────

VALID_POSITION_LEVELS   = {"national", "regional", "local"}
DEFAULT_MIN_CANDIDATE_AGE = 18


# ── Invariants ────────────────────────────────────────────────────────────────

def _require_title_is_not_empty(title: str) -> None:
    if not title:
        raise ValueError("Position title cannot be empty.")


def _require_valid_level(level: str) -> None:
    if level.lower() not in VALID_POSITION_LEVELS:
        raise ValueError(
            f"Invalid level '{level}'. "
            f"Valid levels are: {', '.join(sorted(VALID_POSITION_LEVELS))}"
        )


def _require_valid_seat_count(number_of_winners: int) -> None:
    if number_of_winners <= 0:
        raise ValueError("Number of winners must be at least 1.")


def _require_position_is_not_in_an_open_poll(position_id: int, all_polls: list[dict]) -> None:
    """Raises ValueError if this position is referenced by any currently open poll."""
    for poll in all_polls:
        if poll["status"] != "open":
            continue
        position_ids_in_this_poll = [
            poll_position["position_id"]
            for poll_position in poll.get("positions", [])
        ]
        if position_id in position_ids_in_this_poll:
            raise ValueError(
                f"Cannot deactivate — position is used in open poll: '{poll['title']}'"
            )


def _require_position_is_currently_active(position: dict) -> None:
    if not position["is_active"]:
        raise ValueError(f"Position '{position['title']}' is already inactive.")


# ── Operations ────────────────────────────────────────────────────────────────

class CreatePosition:
    """Validates inputs and creates a new active position."""

    def __init__(self, created_by: str) -> None:
        self._position_store = PositionStore.get()
        self._created_by     = created_by

    def execute(
        self,
        title:              str,
        description:        str,
        level:              str,
        number_of_winners:  int,
        min_candidate_age:  int = DEFAULT_MIN_CANDIDATE_AGE,
    ) -> dict:
        _require_title_is_not_empty(title)
        _require_valid_level(level)
        _require_valid_seat_count(number_of_winners)

        new_position = {
            "title":             title,
            "description":       description,
            "level":             level.capitalize(),
            "max_winners":       number_of_winners,
            "min_candidate_age": min_candidate_age,
            "is_active":         True,
            "created_by":        self._created_by,
            "created_at":        str(datetime.datetime.now()),
        }
        return self._position_store.insert(new_position)


class GetAllPositions:
    """Returns every position in the store."""

    def __init__(self) -> None:
        self._position_store = PositionStore.get()

    def execute(self) -> list[dict]:
        return self._position_store.all()


class GetPosition:
    """Returns a single position by id, or raises ValueError if not found."""

    def __init__(self) -> None:
        self._position_store = PositionStore.get()

    def execute(self, position_id: int) -> dict:
        matching_position = self._position_store.find_one(id=position_id)
        if matching_position is None:
            raise ValueError(f"Position {position_id} not found.")
        return matching_position


class UpdatePosition:
    """Edits allowed fields on an existing position."""

    EDITABLE_FIELDS = {"title", "description", "level", "max_winners"}

    def __init__(self) -> None:
        self._position_store = PositionStore.get()

    def execute(self, position_id: int, requested_changes: dict) -> dict:
        GetPosition().execute(position_id)   # confirms it exists

        # Validate any fields being changed before applying them.
        if "title" in requested_changes:
            _require_title_is_not_empty(requested_changes["title"])

        if "level" in requested_changes:
            _require_valid_level(requested_changes["level"])
            requested_changes["level"] = requested_changes["level"].capitalize()

        if "max_winners" in requested_changes:
            _require_valid_seat_count(requested_changes["max_winners"])

        # Strip out any fields that are not editable through this operation.
        safe_changes = {
            field_name: new_value
            for field_name, new_value in requested_changes.items()
            if field_name in self.EDITABLE_FIELDS and new_value not in (None, "")
        }

        return self._position_store.update(position_id, safe_changes)


class DeactivatePosition:
    """
    Marks a position as inactive so it can no longer be used in new polls.
    Refuses if the position is currently part of an open poll.
    Requires a list of all current polls to check for active usage.
    """

    def __init__(self, all_current_polls: list[dict]) -> None:
        self._position_store  = PositionStore.get()
        self._all_current_polls = all_current_polls

    def execute(self, position_id: int) -> dict:
        position_to_deactivate = GetPosition().execute(position_id)
        _require_position_is_currently_active(position_to_deactivate)
        _require_position_is_not_in_an_open_poll(position_id, self._all_current_polls)
        return self._position_store.update(position_id, {"is_active": False})