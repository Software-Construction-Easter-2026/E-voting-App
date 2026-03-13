"""
Candidate model — Represents an election candidate.

A candidate is a person who has been registered by an admin to
stand for one or more elective positions within a poll. Eligibility
depends on age, education level, and absence of a criminal record.
These rules are enforced by the CandidateService at creation time.
"""

import datetime


class Candidate:
    """Domain entity for an election candidate.

    Attributes:
        id: Unique auto-incremented identifier.
        full_name: Legal full name of the candidate.
        national_id: Government-issued national ID (must be unique).
        date_of_birth: Date string in YYYY-MM-DD format.
        age: Computed age at the time of registration.
        education: Highest education level attained.
        party: Political party or affiliation name.
        has_criminal_record: Candidates with records are rejected.
        is_active: Soft-delete flag (False = deactivated).
        is_approved: Whether the candidate has been approved by admin.
    """

    def __init__(self, candidate_id, full_name, national_id, date_of_birth,
                 age, gender, education, party, manifesto, address, phone,
                 email, has_criminal_record=False, years_experience=0,
                 is_active=True, is_approved=True, created_at=None,
                 created_by=None):
        self.id = candidate_id
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
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def is_eligible_for_position(self, min_age):
        """Check whether this candidate meets the minimum requirements
        to be assigned to a position (must be active, approved, and
        old enough for the specific position)."""
        return self.is_active and self.is_approved and self.age >= min_age

    def deactivate(self):
        """Soft-delete: marks the candidate as inactive rather than
        removing them from the database, preserving vote history."""
        self.is_active = False

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "education": self.education,
            "party": self.party,
            "manifesto": self.manifesto,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "has_criminal_record": self.has_criminal_record,
            "years_experience": self.years_experience,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Candidate instance from a stored dictionary.
        Uses .get() with defaults so older JSON files remain compatible."""
        return cls(
            candidate_id=data["id"],
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=data["age"],
            gender=data["gender"],
            education=data["education"],
            party=data["party"],
            manifesto=data["manifesto"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            has_criminal_record=data.get("has_criminal_record", False),
            years_experience=data.get("years_experience", 0),
            is_active=data.get("is_active", True),
            is_approved=data.get("is_approved", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )