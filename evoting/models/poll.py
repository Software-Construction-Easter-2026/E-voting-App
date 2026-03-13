"""
Poll model - represents an election/poll event.
"""

import datetime


class PollPosition:
    """Represents a position within a poll with assigned candidates."""
    
    def __init__(
        self,
        position_id: int,
        position_title: str,
        candidate_ids: list = None,
        max_winners: int = 1
    ):
        self.position_id = position_id
        self.position_title = position_title
        self.candidate_ids = candidate_ids or []
        self.max_winners = max_winners
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "position_id": self.position_id,
            "position_title": self.position_title,
            "candidate_ids": self.candidate_ids,
            "max_winners": self.max_winners
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PollPosition':
        """Create from dictionary."""
        return cls(
            position_id=data["position_id"],
            position_title=data["position_title"],
            candidate_ids=data.get("candidate_ids", []),
            max_winners=data.get("max_winners", 1)
        )


class Poll:
    """Represents an election/poll with positions and candidates."""
    
    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        election_type: str,
        start_date: str,
        end_date: str,
        positions: list = None,
        station_ids: list = None,
        status: str = "draft",
        total_votes_cast: int = 0,
        created_at: str = None,
        created_by: str = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions or []
        self.station_ids = station_ids or []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self) -> dict:
        """Convert poll to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": [
                p.to_dict() if isinstance(p, PollPosition) else p
                for p in self.positions
            ],
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Poll':
        """Create poll from dictionary."""
        positions = [
            PollPosition.from_dict(p) if isinstance(p, dict) else p
            for p in data.get("positions", [])
        ]
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=positions,
            station_ids=data.get("station_ids", []),
            status=data.get("status", "draft"),
            total_votes_cast=data.get("total_votes_cast", 0),
            created_at=data.get("created_at"),
            created_by=data.get("created_by")
        )
