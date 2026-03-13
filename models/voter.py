"""Voter model for the E-Voting System."""

import datetime


class Voter:
    """Represents a registered voter in the electoral system."""

    def __init__(
        self,
        id=None,
        full_name=None,
        national_id=None,
        date_of_birth=None,
        age=None,
        gender=None,
        address=None,
        phone=None,
        email=None,
        password=None,
        voter_card_number=None,
        station_id=None,
        is_verified=False,
        is_active=True,
        has_voted_in=None,
        role="voter",
        registered_at=None,
    ):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.is_active = is_active
        self.has_voted_in = has_voted_in or []
        self.registered_at = registered_at or str(datetime.datetime.now())
        self.role = role

    def to_dict(self):
        """Convert voter object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a voter object from a dictionary."""
        return cls(**data)

    def can_vote(self):
        """Return True if the voter is verified and active."""
        return self.is_verified and self.is_active

    def has_voted_in_poll(self, poll_id):
        """Check whether the voter has already voted in a given poll."""
        return poll_id in self.has_voted_in

    def add_voted_poll(self, poll_id):
        """Add a poll to the voter's voting history."""
        if poll_id not in self.has_voted_in:
            self.has_voted_in.append(poll_id)