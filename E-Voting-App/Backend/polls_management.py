"""
polls.py

Poll management module.
One class per operation. Each class does exactly one thing.
Data is stored in data/polls.json.

Classes:
    PollStore        — shared JsonStore instance for this module
    CreatePoll       — validates and inserts a new poll
    GetAllPolls      — returns every poll
    GetPoll          — returns one poll by id
    UpdatePoll       — edits a draft or closed poll (no votes)
    DeletePoll       — removes a poll (not if open)
    OpenPoll         — changes status draft → open
    ClosePoll        — changes status open → closed
    AssignCandidates — assigns candidate ids to a position inside a poll
"""

import datetime
from Backend.storage import JsonStore


# ── Shared store ─────────────────────────────────────────────────────────────

class PollStore:
    """Single access point to the polls JSON file for all poll operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/polls.json")
        return cls._instance


# ── Invariants ────────────────────────────────────────────────────────────────
# Plain functions — not UI, not storage — just business rules.

def _require_valid_dates(start_date: str, end_date: str) -> None:
    """Raises ValueError if dates are not YYYY-MM-DD or end is not after start."""
    try:
        parsed_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        parsed_end_date   = datetime.datetime.strptime(end_date,   "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format.")
    if parsed_end_date <= parsed_start_date:
        raise ValueError("End date must be after start date.")


def _require_poll_is_editable(poll: dict) -> None:
    """Raises ValueError if the poll cannot be edited right now."""
    if poll["status"] == "open":
        raise ValueError("Cannot modify an open poll. Close it first.")
    if poll["status"] == "closed" and poll["total_votes"] > 0:
        raise ValueError("Cannot modify a closed poll that already has votes.")


def _require_poll_is_not_open(poll: dict) -> None:
    """Raises ValueError if the poll is currently open."""
    if poll["status"] == "open":
        raise ValueError("Cannot delete an open poll. Close it first.")


def _require_at_least_one_candidate_assigned(poll: dict) -> None:
    """Raises ValueError if no position in the poll has any candidates."""
    any_position_has_candidates = any(
        position["candidate_ids"] for position in poll["positions"]
    )
    if not any_position_has_candidates:
        raise ValueError("Cannot open poll — assign candidates to at least one position first.")


# ── Operations ────────────────────────────────────────────────────────────────

class CreatePoll:
    """Validates inputs and creates a new poll with status 'draft'."""

    def __init__(self, created_by: str) -> None:
        self._poll_store = PollStore.get()
        self._created_by = created_by

    def execute(
        self,
        title: str,
        description: str,
        election_type: str,
        start_date: str,
        end_date: str,
        positions: list[dict],   # [{"position_id": 1, "title": "...", "max_winners": 1}]
        station_ids: list[int],
    ) -> dict:
        if not title:
            raise ValueError("Title cannot be empty.")
        _require_valid_dates(start_date, end_date)
        if not positions:
            raise ValueError("At least one position is required.")

        poll_positions = [
            {
                "position_id":    position["position_id"],
                "position_title": position["title"],
                "max_winners":    position["max_winners"],
                "candidate_ids":  [],
            }
            for position in positions
        ]

        new_poll = {
            "title":         title,
            "description":   description,
            "election_type": election_type,
            "start_date":    start_date,
            "end_date":      end_date,
            "positions":     poll_positions,
            "station_ids":   station_ids,
            "status":        "draft",
            "total_votes":   0,
            "created_by":    self._created_by,
            "created_at":    str(datetime.datetime.now()),
        }
        return self._poll_store.insert(new_poll)


class GetAllPolls:
    """Returns every poll in the store."""

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self) -> list[dict]:
        return self._poll_store.all()


class GetPoll:
    """Returns a single poll by id, or raises ValueError if not found."""

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self, poll_id: int) -> dict:
        matching_poll = self._poll_store.find_one(id=poll_id)
        if matching_poll is None:
            raise ValueError(f"Poll {poll_id} not found.")
        return matching_poll


class UpdatePoll:
    """Edits allowed fields on a draft or closed (no-votes) poll."""

    # Only these fields may be changed through UpdatePoll.
    EDITABLE_FIELDS = {"title", "description", "election_type", "start_date", "end_date"}

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self, poll_id: int, requested_changes: dict) -> dict:
        existing_poll = GetPoll().execute(poll_id)
        _require_poll_is_editable(existing_poll)

        # Strip out any fields that are not allowed to be edited.
        safe_changes = {
            field_name: new_value
            for field_name, new_value in requested_changes.items()
            if field_name in self.EDITABLE_FIELDS and new_value
        }

        # If either date is being changed, re-validate both together.
        if "start_date" in safe_changes or "end_date" in safe_changes:
            updated_start_date = safe_changes.get("start_date", existing_poll["start_date"])
            updated_end_date   = safe_changes.get("end_date",   existing_poll["end_date"])
            _require_valid_dates(updated_start_date, updated_end_date)

        return self._poll_store.update(poll_id, safe_changes)


class DeletePoll:
    """Deletes a poll. Refuses if the poll is currently open."""

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self, poll_id: int) -> str:
        poll_to_delete = GetPoll().execute(poll_id)
        _require_poll_is_not_open(poll_to_delete)
        self._poll_store.delete(poll_id)
        return poll_to_delete["title"]


class OpenPoll:
    """Opens a draft (or re-opens a closed) poll so voting can begin."""

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self, poll_id: int) -> dict:
        poll_to_open = GetPoll().execute(poll_id)
        if poll_to_open["status"] == "open":
            raise ValueError("Poll is already open.")
        _require_at_least_one_candidate_assigned(poll_to_open)
        return self._poll_store.update(poll_id, {"status": "open"})


class ClosePoll:
    """Closes an open poll — no more votes are accepted after this."""

    def __init__(self) -> None:
        self._poll_store = PollStore.get()

    def execute(self, poll_id: int) -> dict:
        poll_to_close = GetPoll().execute(poll_id)
        if poll_to_close["status"] != "open":
            raise ValueError("Poll is not open.")
        return self._poll_store.update(poll_id, {"status": "closed"})


class AssignCandidates:
    """
    Assigns a list of candidate ids to one position inside a poll.
    Silently skips any candidate id that is not in eligible_candidate_ids.
    Only allowed while the poll is in draft status.
    """

    def __init__(self, eligible_candidate_ids: set[int]) -> None:
        self._poll_store           = PollStore.get()
        self._eligible_candidate_ids = eligible_candidate_ids

    def execute(self, poll_id: int, position_index: int, requested_candidate_ids: list[int]) -> dict:
        target_poll = GetPoll().execute(poll_id)
        if target_poll["status"] == "open":
            raise ValueError("Cannot assign candidates to an open poll.")

        validated_candidate_ids = [
            candidate_id for candidate_id in requested_candidate_ids
            if candidate_id in self._eligible_candidate_ids
        ]

        target_poll["positions"][position_index]["candidate_ids"] = validated_candidate_ids
        return self._poll_store.update(poll_id, {"positions": target_poll["positions"]})
