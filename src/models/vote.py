from dataclasses import dataclass
from typing import Optional

@dataclass
class Vote:
    vote_id: str
    poll_id: int
    position_id: int
    candidate_id: Optional[int]
    voter_id: int
    station_id: int
    timestamp: str
    abstained: bool
