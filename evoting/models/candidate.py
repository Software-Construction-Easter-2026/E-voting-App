"""
Candidate model - represents an election candidate.
"""

import datetime


class Candidate:
    """Represents an election candidate with eligibility criteria."""
    
    def __init__(
        self,
        id: int,
        full_name: str,
        national_id: str,
        date_of_birth: str,
        age: int,
        gender: str,
        education: str,
        party: str,
        manifesto: str,
        address: str,
        phone: str,
        email: str,
        has_criminal_record: bool,
        years_experience: int,
        is_active: bool = True,
        is_approved: bool = True,
        created_at: str = None,
        created_by: str = None
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
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self) -> dict:
        """Convert candidate to dictionary for storage."""
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
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Candidate':
        """Create candidate from dictionary."""
        return cls(
            id=data["id"],
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
            has_criminal_record=data["has_criminal_record"],
            years_experience=data["years_experience"],
            is_active=data.get("is_active", True),
            is_approved=data.get("is_approved", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by")
        )
