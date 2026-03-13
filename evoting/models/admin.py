"""
Admin model - represents an administrator account.
"""

import datetime


class Admin:
    """Represents an administrator in the system."""
    
    def __init__(
        self,
        id: int,
        username: str,
        password: str,
        full_name: str,
        email: str,
        role: str,
        created_at: str = None,
        is_active: bool = True
    ):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at or str(datetime.datetime.now())
        self.is_active = is_active
    
    def to_dict(self) -> dict:
        """Convert admin to dictionary for storage."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Admin':
        """Create admin from dictionary."""
        return cls(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            created_at=data.get("created_at"),
            is_active=data.get("is_active", True)
        )
