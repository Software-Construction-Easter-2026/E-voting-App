"""
VotingStation model - represents a physical voting location.
"""

import datetime


class VotingStation:
    """Represents a physical voting station/location."""
    
    def __init__(
        self,
        id: int,
        name: str,
        location: str,
        region: str,
        capacity: int,
        registered_voters: int = 0,
        supervisor: str = "",
        contact: str = "",
        opening_time: str = "",
        closing_time: str = "",
        is_active: bool = True,
        created_at: str = None,
        created_by: str = None
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
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self) -> dict:
        """Convert station to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "region": self.region,
            "capacity": self.capacity,
            "registered_voters": self.registered_voters,
            "supervisor": self.supervisor,
            "contact": self.contact,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VotingStation':
        """Create station from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            location=data["location"],
            region=data["region"],
            capacity=data["capacity"],
            registered_voters=data.get("registered_voters", 0),
            supervisor=data.get("supervisor", ""),
            contact=data.get("contact", ""),
            opening_time=data.get("opening_time", ""),
            closing_time=data.get("closing_time", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by")
        )
