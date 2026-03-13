"""
Vote model - represents a single vote cast.
"""


class Vote:
    """Represents a single vote cast by a voter."""
    
    def __init__(
        self,
        vote_id: str,
        poll_id: int,
        position_id: int,
        candidate_id: int,
        voter_id: int,
        station_id: int,
        timestamp: str,
        abstained: bool = False
    ):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp
        self.abstained = abstained
    
    def to_dict(self) -> dict:
        """Convert vote to dictionary for storage."""
        return {
            "vote_id": self.vote_id,
            "poll_id": self.poll_id,
            "position_id": self.position_id,
            "candidate_id": self.candidate_id,
            "voter_id": self.voter_id,
            "station_id": self.station_id,
            "timestamp": self.timestamp,
            "abstained": self.abstained
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Vote':
        """Create vote from dictionary."""
        return cls(
            vote_id=data["vote_id"],
            poll_id=data["poll_id"],
            position_id=data["position_id"],
            candidate_id=data["candidate_id"],
            voter_id=data["voter_id"],
            station_id=data["station_id"],
            timestamp=data["timestamp"],
            abstained=data.get("abstained", False)
        )
