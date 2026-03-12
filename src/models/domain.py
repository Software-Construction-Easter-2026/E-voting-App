from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Candidate:
    id: int
    full_name: str
    national_id: str
    date_of_birth: str
    age: int
    gender: str
    education: str
    party: str
    manifesto: str
    address: str
    phone: str
    email: str
    has_criminal_record: bool
    years_experience: int
    is_active: bool = True
    is_approved: bool = True
    created_at: str = field(default_factory=lambda: str(datetime.now()))
    created_by: str = ""

@dataclass
class Position:
    id: int
    title: str
    description: str
    level: str
    max_winners: int
    min_candidate_age: int
    is_active: bool = True
    created_at: str = field(default_factory=lambda: str(datetime.now()))
    created_by: str = ""

@dataclass
class PollPosition:
    position_id: int
    position_title: str
    max_winners: int
    candidate_ids: list[int] = field(default_factory=list)

@dataclass
class Poll:
    id: int
    title: str
    description: str
    election_type: str
    start_date: str
    end_date: str
    positions: list[dict] = field(default_factory=list)
    station_ids: list[int] = field(default_factory=list)
    status: str = "draft"
    total_votes_cast: int = 0
    created_at: str = field(default_factory=lambda: str(datetime.now()))
    created_by: str = ""

@dataclass
class Station:
    id: int
    name: str
    location: str
    region: str
    capacity: int
    registered_voters: int
    supervisor: str
    contact: str
    opening_time: str
    closing_time: str
    is_active: bool = True
    created_at: str = field(default_factory=lambda: str(datetime.now()))
    created_by: str = ""
