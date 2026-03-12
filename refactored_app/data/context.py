"""Context that holds the store and all repositories. Passed to services."""

from .store import DataStore
from .repository import (
    CandidateRepository,
    StationRepository,
    PositionRepository,
    PollRepository,
    VoterRepository,
    AdminRepository,
    VoteRepository,
    AuditRepository,
)


class DataContext:
    def __init__(self):
        self.store = DataStore()
        self.candidates = CandidateRepository(self.store)
        self.stations = StationRepository(self.store)
        self.positions = PositionRepository(self.store)
        self.polls = PollRepository(self.store)
        self.voters = VoterRepository(self.store)
        self.admins = AdminRepository(self.store)
        self.votes = VoteRepository(self.store)
        self.audit = AuditRepository(self.store)
