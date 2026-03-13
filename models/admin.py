"""Admin model for the E-Voting System"""
'''This model represents system adminstrators with different levels of permission'''
import datetime

class Admin:
    """Represents an administrator account"""
    
    def __init__(self, id=None, username=None, password=None, full_name=None,
                 email=None, role=None, is_active=True):
        
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = str(datetime.datetime.now())
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        """Create Admin from dictionary"""
        admin = cls()
        for key, value in data.items():
            setattr(admin, key, value)
        return admin
    
    def can_manage_admins(self):
        """Check if admin can manage other admin accounts"""
        return self.role == "super_admin"
    
    def can_manage_polls(self):
        """Check if admin can manage polls"""
        return self.role in ["super_admin", "election_officer"]
    
    def can_manage_stations(self):
        """Check if admin can manage stations"""
        return self.role in ["super_admin", "station_manager"]
    
    def can_view_audit(self):
        """Check if admin can view audit logs"""
        return self.role in ["super_admin", "auditor"]