"""
Vote model — Represents a single ballot cast by a voter.

Each Vote records one choice for one position within a poll. A voter
casting a ballot in a poll with 3 positions creates 3 Vote records.
Votes are immutable once created — they are never updated or deleted
(except when an entire poll is deleted).

The vote_id is a composite of a truncated SHA-256 hash (receipt) and
the position_id, ensuring uniqueness per voter-poll-position.
"""


class Vote:
    """Domain entity for a single ballot entry.

    Attributes:
        vote_id: Unique identifier (hash + position_id).
        poll_id: Which poll this vote belongs to.
        position_id: Which position this vote is for.
        candidate_id: The chosen candidate's ID, or None if abstained.
        voter_id: The voter who cast this ballot.
        station_id: The station the voter is registered at.
        timestamp: When the vote was recorded.
        abstained: True if the voter chose to skip this position.
    """

    def __init__(self, vote_id, poll_id, position_id, candidate_id,
                 voter_id, station_id, timestamp, abstained=False):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp
        self.abstained = abstained

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "vote_id": self.vote_id,
            "poll_id": self.poll_id,
            "position_id": self.position_id,
            "candidate_id": self.candidate_id,
            "voter_id": self.voter_id,
            "station_id": self.station_id,
            "timestamp": self.timestamp,
            "abstained": self.abstained,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Vote instance from a stored dictionary."""
        return cls(
            vote_id=data["vote_id"],
            poll_id=data["poll_id"],
            position_id=data["position_id"],
            candidate_id=data["candidate_id"],
            voter_id=data["voter_id"],
            station_id=data["station_id"],
            timestamp=data["timestamp"],
            abstained=data.get("abstained", False),
        )