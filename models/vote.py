"""Vote model for the E-Voting System"""
'''This module defines the Vote class which represents a single vote cast
by a voter for a specific position in a poll.'''
import datetime

class Vote:
    """Represents a cast vote"""
    
    def __init__(self, vote_id=None, poll_id=None, position_id=None,
                 candidate_id=None, voter_id=None, station_id=None,
                 timestamp=None, abstained=False):
        
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp or str(datetime.datetime.now())
        self.abstained = abstained
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Vote from dictionary"""
        vote = cls()
        for key, value in data.items():
            setattr(vote, key, value)
        return vote