"""Voting Station model for the E-Voting System."""

import datetime


class VotingStation:
    """Represents a physical voting station where voters cast ballots."""

    def __init__(
        self,
        id=None,
        name=None,
        location=None,
        region=None,
        capacity=0,
        registered_voters=0,
        supervisor=None,
        contact=None,
        opening_time=None,
        closing_time=None,
        is_active=True,
        created_by=None,
        created_at=None,
    ):
        self.id = id
        self.name = name
        self.location = location
        self.region = region
        self.capacity = capacity
        self.registered_voters = registered_voters
        self.supervisor = supervisor
        self.contact = contact
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_active = is_active
        self.created_by = created_by
        self.created_at = created_at or str(datetime.datetime.now())

    def to_dict(self):
        """Convert station object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a VotingStation object from a dictionary."""
        return cls(**data)

    def get_load_percentage(self):
        """Return the percentage of registered voters relative to capacity."""
        if self.capacity <= 0:
            return 0
        return (self.registered_voters / self.capacity) * 100

    def get_load_status(self):
        """Return a simple load status for the station."""
        load = self.get_load_percentage()

        if load > 100:
            return "OVERLOADED"
        elif load > 75:
            return "HIGH"
        elif load > 50:
            return "MEDIUM"
        else:
            return "OK"