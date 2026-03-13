"""
Voter model - represents a registered voter.
"""

import datetime


class Voter:
    """Represents a registered voter in the system."""
    
    def __init__(
        self,
        id: int,
        full_name: str,
        national_id: str,
        date_of_birth: str,
        age: int,
        gender: str,
        address: str,
        phone: str,
        email: str,
        password: str,
        voter_card_number: str,
        station_id: int,
        is_verified: bool = False,
        is_active: bool = True,
        has_voted_in: list = None,
        registered_at: str = None,
        role: str = "voter"
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
    
    def to_dict(self) -> dict:
        """Convert voter to dictionary for storage."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "password": self.password,
            "voter_card_number": self.voter_card_number,
            "station_id": self.station_id,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "has_voted_in": self.has_voted_in,
            "registered_at": self.registered_at,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Voter':
        """Create voter from dictionary."""
        return cls(
            id=data["id"],
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=data["age"],
            gender=data["gender"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            password=data["password"],
            voter_card_number=data["voter_card_number"],
            station_id=data["station_id"],
            is_verified=data.get("is_verified", False),
            is_active=data.get("is_active", True),
            has_voted_in=data.get("has_voted_in", []),
            registered_at=data.get("registered_at"),
            role=data.get("role", "voter")
        )
