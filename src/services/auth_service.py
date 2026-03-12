import hashlib

class AuthService:
    def __init__(self, data_store):
        self.ds = data_store
        
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login_admin(self, username, password):
        hashed = self.hash_password(password)
        for admin in self.ds.admins.values():
            if admin.username == username and admin.password == hashed:
                if not admin.is_active:
                    self.ds.log_action("LOGIN_FAILED", username, "Account deactivated")
                    return False, "This account has been deactivated.", None
                
                self.ds.log_action("LOGIN", username, "Admin login successful")
                return True, f"Welcome, {admin.full_name}!", admin

        self.ds.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
        return False, "Invalid credentials.", None

    def login_voter(self, voter_card, password):
        hashed = self.hash_password(password)
        for voter in self.ds.voters.values():
            if voter.voter_card_number == voter_card and voter.password == hashed:
                if not voter.is_active:
                    self.ds.log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                    return False, "This voter account has been deactivated.", None
                if not voter.is_verified:
                    self.ds.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                    return False, "Your voter registration has not been verified yet.\nPlease contact an admin to verify your registration.", None
                
                self.ds.log_action("LOGIN", voter_card, "Voter login successful")
                return True, f"Welcome, {voter.full_name}!", voter
        
        self.ds.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        return False, "Invalid voter card number or password.", None
