"""
Admin model — Represents an administrator account.

The system supports four admin roles with different access levels:
  - super_admin: Full access to all features including admin management.
  - election_officer: Can manage polls and candidates.
  - station_manager: Can manage stations and verify voters.
  - auditor: Read-only access to reports and audit logs.

Role-based access checks are handled in the UI layer; the model
only stores the role string and provides a convenience check.
"""

import datetime


class Admin:
    """Domain entity for an administrator account.

    Attributes:
        id: Unique auto-incremented identifier.
        username: Login username (must be unique across all admins).
        password: SHA-256 hash of the admin's password.
        role: One of 'super_admin', 'election_officer',
              'station_manager', or 'auditor'.
        is_active: Soft-delete flag.
    """

    def __init__(self, admin_id, username, password, full_name, email, role,
                 created_at=None, is_active=True):
        self.id = admin_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at or str(datetime.datetime.now())
        self.is_active = is_active

    def is_super_admin(self):
        """Only super admins can create/deactivate other admin accounts."""
        return self.role == "super_admin"

    def deactivate(self):
        """Soft-delete: disables the admin account."""
        self.is_active = False

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct an Admin instance from a stored dictionary."""
        return cls(
            admin_id=data["id"],
            username=data["username"],
            password=data["password"],
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            created_at=data.get("created_at"),
            is_active=data.get("is_active", True),
        )