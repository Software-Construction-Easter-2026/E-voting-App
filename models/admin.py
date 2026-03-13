"""Admin model for the E-Voting System."""

import datetime


class Admin:
    """Represents a system administrator with specific permissions."""

    def __init__(
        self,
        id=None,
        username=None,
        password=None,
        full_name=None,
        email=None,
        role=None,
        is_active=True,
        created_at=None,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or str(datetime.datetime.now())

    def to_dict(self):
        """Convert admin object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create an Admin object from a dictionary."""
        return cls(**data)

    def can_manage_admins(self):
        """Return True if the admin can manage other admins."""
        return self.role == "super_admin"

    def can_manage_polls(self):
        """Return True if the admin can manage polls."""
        return self.role in ["super_admin", "election_officer"]

    def can_manage_stations(self):
        """Return True if the admin can manage voting stations."""
        return self.role in ["super_admin", "station_manager"]

    def can_view_audit(self):
        """Return True if the admin can view audit logs."""
        return self.role in ["super_admin", "auditor"]