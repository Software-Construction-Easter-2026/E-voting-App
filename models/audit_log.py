"""Audit Log model for the E-Voting System"""
'''This module defines the AuditLog class which records important system
actions for accountability and auditing purposes.'''
import datetime

class AuditLog:
    """Represents an audit log entry"""
    
    def __init__(self, action=None, user=None, details=None, timestamp=None):
        self.action = action
        self.user = user
        self.details = details
        self.timestamp = timestamp or str(datetime.datetime.now())
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create AuditLog from dictionary"""
        log = cls()
        for key, value in data.items():
            setattr(log, key, value)
        return log