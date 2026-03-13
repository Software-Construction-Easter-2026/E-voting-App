"""
Position model — Represents an elective position (e.g. President, Governor).

Positions define what roles candidates can compete for within a poll.
Each position specifies a level (National/Regional/Local), the number
of available seats (max_winners), and a minimum candidate age threshold.
"""

import datetime

from e_voting.constants import MIN_CANDIDATE_AGE


class Position:
    """Domain entity for an elective position.

    Attributes:
        id: Unique auto-incremented identifier.
        title: Name of the position (e.g. "President", "Senator").
        level: Governance level — "National", "Regional", or "Local".
        max_winners: How many seats are available (e.g. 1 for President).
        min_candidate_age: Minimum age a candidate must meet for this
                           specific position (may differ from the global
                           MIN_CANDIDATE_AGE).
        is_active: Soft-delete flag.
    """

    def __init__(self, position_id, title, description, level, max_winners,
                 min_candidate_age=MIN_CANDIDATE_AGE,
                 is_active=True, created_at=None, created_by=None):
        self.id = position_id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def deactivate(self):
        """Soft-delete: marks the position as inactive."""
        self.is_active = False

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "max_winners": self.max_winners,
            "min_candidate_age": self.min_candidate_age,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Position instance from a stored dictionary."""
        return cls(
            position_id=data["id"],
            title=data["title"],
            description=data["description"],
            level=data["level"],
            max_winners=data["max_winners"],
            min_candidate_age=data.get("min_candidate_age", MIN_CANDIDATE_AGE),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )