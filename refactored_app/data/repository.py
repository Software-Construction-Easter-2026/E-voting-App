"""Repository layer: abstract access to entities. Services use these instead of the store directly."""

from .store import DataStore


class BaseRepository:
    """Base repository providing shared functionality."""

    def __init__(self, store: DataStore, collection_name: str, counter_name: str = None):
        self._store = store
        self._collection_name = collection_name
        self._counter_name = counter_name

    def _collection(self):
        return getattr(self._store, self._collection_name)

    def get_all(self):
        return self._collection()

    def get_by_id(self, entity_id: int):
        return self._collection().get(entity_id)

    def add(self, entity_id: int, data: dict):
        self._collection()[entity_id] = data

    def next_id(self) -> int:
        if not self._counter_name:
            raise ValueError("This repository does not support ID generation")

        counter = getattr(self._store, self._counter_name)
        setattr(self._store, self._counter_name, counter + 1)
        return counter


class CandidateRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "candidates", "candidate_id_counter")


class StationRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "voting_stations", "station_id_counter")


class PositionRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "positions", "position_id_counter")


class PollRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "polls", "poll_id_counter")

    def remove(self, pid: int):
        self._collection().pop(pid, None)


class VoterRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "voters", "voter_id_counter")


class AdminRepository(BaseRepository):
    def __init__(self, store: DataStore):
        super().__init__(store, "admins", "admin_id_counter")


class VoteRepository:
    """Votes stored as list because each vote is unique."""

    def __init__(self, store: DataStore):
        self._store = store

    def get_all(self):
        return self._store.votes

    def append(self, vote: dict):
        self._store.votes.append(vote)

    def remove_by_poll_id(self, poll_id: int):
        self._store.votes = [
            v for v in self._store.votes
            if v["poll_id"] != poll_id
        ]


class AuditRepository:
    """Audit log repository."""

    def __init__(self, store: DataStore):
        self._store = store

    def get_all(self):
        return self._store.audit_log

    def append(self, entry: dict):
        self._store.audit_log.append(entry)