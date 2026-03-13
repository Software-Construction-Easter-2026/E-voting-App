"""Position model for the E-Voting System."""

import datetime


class Position:
    """Represents an electoral position (e.g., President, Minister, Chairman LC5)."""

    def __init__(
        self,
        id=None,
        title=None,
        description=None,
        level=None,
        max_winners=1,
        min_candidate_age=25,
        is_active=True,
        created_by=None,
        created_at=None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_by = created_by
        self.created_at = created_at or str(datetime.datetime.now())

    def to_dict(self):
        """Convert position object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a Position object from a dictionary."""
        return cls(**data)

    def __str__(self):
        """Return a readable string representation of the position."""
        return f"{self.title} ({self.level}) - {self.max_winners} seat(s)"