"""Audit Log model for the E-Voting System."""

import datetime


class AuditLog:
    """Represents a single audit log entry for system actions."""

    def __init__(self, action=None, user=None, details=None, timestamp=None):
        self.action = action
        self.user = user
        self.details = details
        self.timestamp = timestamp or str(datetime.datetime.now())

    def to_dict(self):
        """Convert audit log object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Create an AuditLog object from a dictionary."""
        return cls(**data)