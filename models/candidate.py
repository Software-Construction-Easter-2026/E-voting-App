"""Candidate model for the E-Voting System."""

import datetime


class Candidate:
    """Represents a political candidate in the electoral system."""

    def __init__(
        self,
        id=None,
        full_name=None,
        national_id=None,
        date_of_birth=None,
        age=None,
        gender=None,
        education=None,
        party=None,
        manifesto=None,
        address=None,
        phone=None,
        email=None,
        has_criminal_record=False,
        years_experience=0,
        is_active=True,
        is_approved=True,
        created_by=None,
        created_at=None,
    ):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto = manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.has_criminal_record = has_criminal_record
        self.years_experience = years_experience
        self.is_active = is_active
        self.is_approved = is_approved
        self.created_by = created_by
        self.created_at = created_at or str(datetime.datetime.now())

    def to_dict(self):
        """Convert candidate object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create a candidate object from a dictionary."""
        return cls(**data)

    def is_eligible(self, min_age=25):
        """Check whether the candidate meets the minimum eligibility rules."""
        return (
            self.is_active
            and self.is_approved
            and not self.has_criminal_record
            and self.age >= min_age
        )

    def display_name(self):
        """Return the candidate name together with party."""
        return f"{self.full_name} ({self.party})"