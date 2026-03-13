"""Candidate model for the E-Voting System, this module defines the Candidate class which represents a person
running for political office in an election."""
import datetime

class Candidate:
    """Represents a political candidate"""
    
    def __init__(self, id=None, full_name=None, national_id=None, 
                 date_of_birth=None, age=None, gender=None, education=None,
                 party=None, manifesto=None, address=None, phone=None, email=None,
                 has_criminal_record=False, years_experience=0, 
                 is_active=True, is_approved=True, created_by=None):
        
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto = manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.has_criminal_record = has_criminal_record
        self.years_experience = years_experience
        self.is_active = is_active
        self.is_approved = is_approved
        self.created_at = str(datetime.datetime.now())
        self.created_by = created_by
    
    def to_dict(self):
        """Convert to a dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Candidate from dictionary"""
        candidate = cls()
        for key, value in data.items():
            setattr(candidate, key, value)
        return candidate
    
    def is_eligible(self, min_age=25):
        """Check if candidate meets eligibility test"""
        return (self.is_active and self.is_approved and 
                not self.has_criminal_record and 
                self.age >= min_age)
    
    def display_name(self):
        """Get a formatted name with party"""
        return f"{self.full_name} ({self.party})"