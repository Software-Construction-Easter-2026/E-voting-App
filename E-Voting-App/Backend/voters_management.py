"""
voters.py

Voter management module.
One class per operation. Data is stored in data/voters.json.

Classes:
    VoterStore       — shared JsonStore instance for this module
    GetAllVoters     — returns every voter
    GetVoter         — returns one voter by id
    VerifyVoter      — marks a single voter as verified
    VerifyAllVoters  — marks every unverified voter as verified
    DeactivateVoter  — deactivates a voter account
    SearchVoters     — searches voters by name, card number, national id, or station
"""

from Backend.storage import JsonStore


# ── Shared store ─────────────────────────────────────────────────────────────

class VoterStore:
    """Single access point to the voters JSON file for all voter operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/voters.json")
        return cls._instance


# ── Invariants ────────────────────────────────────────────────────────────────

def _require_voter_is_active(voter: dict) -> None:
    if not voter["is_active"]:
        raise ValueError(f"Voter '{voter['full_name']}' is already deactivated.")


def _require_voter_is_not_yet_verified(voter: dict) -> None:
    if voter["is_verified"]:
        raise ValueError(f"Voter '{voter['full_name']}' is already verified.")


def _require_voter_can_cast_a_vote(voter: dict) -> None:
    """Called before recording a vote — voter must be verified and active."""
    if not voter["is_verified"]:
        raise ValueError(f"Voter '{voter['full_name']}' is not verified.")
    if not voter["is_active"]:
        raise ValueError(f"Voter '{voter['full_name']}' account is inactive.")


# ── Operations ────────────────────────────────────────────────────────────────

class GetAllVoters:
    """Returns every registered voter."""

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self) -> list[dict]:
        return self._voter_store.all()


class GetVoter:
    """Returns a single voter by id, or raises ValueError if not found."""

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self, voter_id: int) -> dict:
        matching_voter = self._voter_store.find_one(id=voter_id)
        if matching_voter is None:
            raise ValueError(f"Voter {voter_id} not found.")
        return matching_voter


class VerifyVoter:
    """Marks a single voter as verified so they may vote."""

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self, voter_id: int) -> dict:
        voter_to_verify = GetVoter().execute(voter_id)
        _require_voter_is_not_yet_verified(voter_to_verify)
        return self._voter_store.update(voter_id, {"is_verified": True})


class VerifyAllVoters:
    """Marks every currently unverified voter as verified.
       Returns the number of voters that were changed.
    """

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self) -> int:
        unverified_voters = self._voter_store.find(is_verified=False)
        for unverified_voter in unverified_voters:
            self._voter_store.update(unverified_voter["id"], {"is_verified": True})
        return len(unverified_voters)


class DeactivateVoter:
    """Deactivates a voter account so they can no longer vote."""

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self, voter_id: int) -> dict:
        voter_to_deactivate = GetVoter().execute(voter_id)
        _require_voter_is_active(voter_to_deactivate)
        return self._voter_store.update(voter_id, {"is_active": False})


class SearchVoters:
    """
    Searches voters by a chosen field.
    Supported search fields: "name", "card", "national_id", "station"
    """

    SUPPORTED_SEARCH_FIELDS = {"name", "card", "national_id", "station"}

    def __init__(self) -> None:
        self._voter_store = VoterStore.get()

    def execute(self, search_field: str, search_term: str) -> list[dict]:
        if search_field not in self.SUPPORTED_SEARCH_FIELDS:
            raise ValueError(
                f"Unknown search field '{search_field}'. "
                f"Choose from: {self.SUPPORTED_SEARCH_FIELDS}"
            )

        all_voters = self._voter_store.all()

        if search_field == "name":
            return [
                voter for voter in all_voters
                if search_term.lower() in voter["full_name"].lower()
            ]

        if search_field == "card":
            return [
                voter for voter in all_voters
                if voter["voter_card_number"] == search_term
            ]

        if search_field == "national_id":
            return [
                voter for voter in all_voters
                if voter["national_id"] == search_term
            ]

        if search_field == "station":
            try:
                station_id = int(search_term)
            except ValueError:
                raise ValueError("Station ID must be a number.")
            return [
                voter for voter in all_voters
                if voter["station_id"] == station_id
            ]


