"""Poll model for the E-Voting System."""

import datetime


class Poll:
    """Represents an election event."""

    def __init__(
        self,
        id=None,
        title=None,
        description=None,
        election_type=None,
        start_date=None,
        end_date=None,
        positions=None,
        station_ids=None,
        status="draft",
        total_votes_cast=0,
        created_by=None,
        created_at=None,
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
        self.created_by = created_by
        self.created_at = created_at or str(datetime.datetime.now())

    def to_dict(self):
        """Convert poll object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a poll object from a dictionary."""
        return cls(**data)

    def is_open(self):
        """Return True if the poll is open."""
        return self.status == "open"

    def is_closed(self):
        """Return True if the poll is closed."""
        return self.status == "closed"

    def is_draft(self):
        """Return True if the poll is still in draft state."""
        return self.status == "draft"

    def get_position_by_id(self, position_id):
        """Return the position dictionary matching the given ID."""
        for pos in self.positions:
            if pos.get("position_id") == position_id:
                return pos
        return None