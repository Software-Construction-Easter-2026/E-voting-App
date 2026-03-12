from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    full_name: str
    email: str
    password: str
    is_active: bool = True
    role: str = ""

@dataclass
class Admin(User):
    username: str = ""
    created_at: str = field(default_factory=lambda: str(datetime.now()))

@dataclass
class Voter(User):
    national_id: str = ""
    voter_card_number: str = ""
    date_of_birth: str = ""
    age: int = 0
    gender: str = ""
    address: str = ""
    phone: str = ""
    station_id: int = 0
    is_verified: bool = False
    has_voted_in: list[int] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: str(datetime.now()))
