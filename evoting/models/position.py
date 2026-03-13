"""
Position model - represents an electable position.
"""

import datetime
from ..config import MIN_CANDIDATE_AGE


class Position:
    """Represents an electable position (e.g., President, Governor)."""
    
    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        level: str,
        max_winners: int,
        min_candidate_age: int = MIN_CANDIDATE_AGE,
        is_active: bool = True,
        created_at: str = None,
        created_by: str = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self) -> dict:
        """Convert position to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "max_winners": self.max_winners,
            "min_candidate_age": self.min_candidate_age,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create position from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            level=data["level"],
            max_winners=data["max_winners"],
            min_candidate_age=data.get("min_candidate_age", MIN_CANDIDATE_AGE),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by")
        )
