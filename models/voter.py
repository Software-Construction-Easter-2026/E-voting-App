"""Voter model for the E-Voting System """
'''This module defines the Voter class which represents a registered
voter in the electoral system.'''
import datetime

class Voter:
    """Represents a registered voter"""
    '''The voter has different attributes ie id, age, gender as seen below'''
    def __init__(self, id=None, full_name=None, national_id=None, 
                 date_of_birth=None, age=None, gender=None, address=None,
                 phone=None, email=None, password=None, voter_card_number=None,
                 station_id=None, is_verified=False, is_active=True, 
                 has_voted_in=None, role="voter"):
        
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.is_active = is_active
        self.has_voted_in = has_voted_in or []
        self.registered_at = str(datetime.datetime.now())
        self.role = role
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Voter from dictionary"""
        voter = cls()
        for key, value in data.items():
            setattr(voter, key, value)
        return voter
    
    def can_vote(self):
        """Check if voter can vote"""
        return self.is_verified and self.is_active
    
    def has_voted_in_poll(self, poll_id):
        """Check if voter has already voted in a specific poll"""
        return poll_id in self.has_voted_in
    
    def add_voted_poll(self, poll_id):
        """Add a poll to voter's voting history"""
        if poll_id not in self.has_voted_in:
            self.has_voted_in.append(poll_id)