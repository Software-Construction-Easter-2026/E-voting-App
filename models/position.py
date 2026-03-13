"""Position model for the E-Voting System"""
import datetime

class Position:
    """Represents an electoral position (President, Minister, Chairman LC5 etc.)"""
    
    def __init__(self, id=None, title=None, description=None, level=None,
                 max_winners=1, min_candidate_age=25, is_active=True, created_by=None):
        
        self.id = id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_at = str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Position from dictionary"""
        position = cls()
        for key, value in data.items():
            setattr(position, key, value)
        return position
    
    def __str__(self):
        return f"{self.title} ({self.level}) - {self.max_winners} seat(s)"