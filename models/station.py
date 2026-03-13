"""Voting Station model for the E-Voting System"""
'''This module defines the PollingStation class which represents physical
locations where voters cast their ballots.'''
import datetime

class VotingStation:
    """Represents a physical voting station"""
    
    def __init__(self, id=None, name=None, location=None, region=None,
                 capacity=0, registered_voters=0, supervisor=None,
                 contact=None, opening_time=None, closing_time=None,
                 is_active=True, created_by=None):
        
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
        self.created_at = str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create VotingStation from dictionary"""
        station = cls()
        for key, value in data.items():
            setattr(station, key, value)
        return station
    
    def get_load_percentage(self):
        """Get current voter load percentage"""
        if self.capacity <= 0:
            return 0
        return (self.registered_voters / self.capacity) * 100
    
    def get_load_status(self):
        """Get load status as string"""
        load = self.get_load_percentage()
        if load > 100:
            return "OVERLOADED"
        elif load > 75:
            return "HIGH"
        elif load > 50:
            return "MEDIUM"
        else:
            return "OK"