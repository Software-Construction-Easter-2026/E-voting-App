"""Poll model for the E-Voting System"""
'''module defines the Poll class which represents election events
with specific time periods, positions, and assigned stations.'''
import datetime

class Poll:
    """Represents an election/poll"""
    
    def __init__(self, id=None, title=None, description=None, election_type=None,
                 start_date=None, end_date=None, positions=None, station_ids=None,
                 status="draft", total_votes_cast=0, created_by=None):
        
        self.id = id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions or []  # List of dicts with position_id, candidate_ids
        self.station_ids = station_ids or []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Poll from dictionary"""
        poll = cls()
        for key, value in data.items():
            setattr(poll, key, value)
        return poll
    
    def is_open(self):
        """Check if poll is open"""
        return self.status == "open"
    
    def is_closed(self):
        """Check if poll is closed"""
        return self.status == "closed"
    
    def is_draft(self):
        """Check if poll is in draft state"""
        return self.status == "draft"
    
    def get_position_by_id(self, position_id):
        """Get position dict by ID"""
        for pos in self.positions:
            if pos.get("position_id") == position_id:
                return pos
        return None