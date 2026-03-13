"""Vote model for the E-Voting System."""

import datetime


class Vote:
    """Represents a single vote cast in a poll."""

    def __init__(
        self,
        vote_id=None,
        poll_id=None,
        position_id=None,
        candidate_id=None,
        voter_id=None,
        station_id=None,
        timestamp=None,
        abstained=False,
    ):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp or str(datetime.datetime.now())
        self.abstained = abstained

    def to_dict(self):
        """Convert vote object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a Vote object from a dictionary."""
        return cls(**data)