from datetime import datetime
import random
import string
from src.models.user import Voter
from src.services.auth_service import AuthService

class VoterService:
    MIN_VOTER_AGE = 18

    def __init__(self, data_store):
        self.ds = data_store

    def generate_voter_card_number(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def _get_voter_by_id_or_card(self, identifier):
        # 1. Try finding by database ID
        try:
            vid = int(identifier)
            if vid in self.ds.voters:
                return self.ds.voters[vid]
        except (ValueError, TypeError):
            pass

        # 2. Try finding by Voter Card Number
        for v in self.ds.voters.values():
            if v.voter_card_number == identifier:
                return v
        return None

    def get_all_active_stations(self):
        return {sid: s for sid, s in self.ds.voting_stations.items() if s.is_active}

    def register_voter(self, full_name, national_id, dob_str, gender, address, phone, email, password, station_choice):
        # 1. Validation
        if not full_name: return False, "Name cannot be empty."
        if not national_id: return False, "National ID cannot be empty."
        
        for v in self.ds.voters.values():
            if v.national_id == national_id:
                return False, "A voter with this National ID already exists."

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.now() - dob).days // 365
            if age < self.MIN_VOTER_AGE:
                return False, f"You must be at least {self.MIN_VOTER_AGE} years old to register."
        except ValueError:
            return False, "Invalid date format."

        if gender not in ["M", "F", "OTHER"]:
            return False, "Invalid gender selection."
            
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        if station_choice not in self.ds.voting_stations or not self.ds.voting_stations[station_choice].is_active:
             return False, "Invalid station selection."

        # 2. Creation
        voter_card = self.generate_voter_card_number()
        vid = self.ds.voter_id_counter
        
        voter = Voter(
            id=vid,
            full_name=full_name,
            email=email,
            password=AuthService.hash_password(password),
            is_active=True,
            role="voter",
            national_id=national_id,
            voter_card_number=voter_card,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            address=address,
            phone=phone,
            station_id=station_choice,
            is_verified=False,
            has_voted_in=[],
            registered_at=str(datetime.now())
        )
        
        self.ds.voters[vid] = voter
        self.ds.voter_id_counter += 1
        
        self.ds.log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        self.ds.save_data()
        
        return True, voter_card
        
    def get_all_voters(self):
        return self.ds.voters
        
    def verify_voter(self, admin_username, identifier):
        voter = self._get_voter_by_id_or_card(identifier)
        if not voter:
            return False, "Voter not found. Please enter a valid ID or Card Number."
            
        if voter.is_verified:
            return False, f"Voter '{voter.full_name}' is already verified."
            
        voter.is_verified = True
        self.ds.log_action("VERIFY_VOTER", admin_username, f"Verified voter: {voter.full_name} (Card: {voter.voter_card_number})")
        self.ds.save_data()
        return True, f"Voter '{voter.full_name}' verified successfully!"

    def verify_all_pending(self, admin_username):
        count = 0
        for voter in self.ds.voters.values():
            if not voter.is_verified:
                voter.is_verified = True
                count += 1
        if count > 0:
            self.ds.log_action("VERIFY_ALL_VOTERS", admin_username, f"Verified {count} voters")
            self.ds.save_data()
        return count

    def deactivate_voter(self, admin_username, identifier):
        voter = self._get_voter_by_id_or_card(identifier)
        if not voter:
            return False, "Voter not found."
            
        if not voter.is_active:
            return False, f"Voter '{voter.full_name}' is already deactivated."
            
        voter.is_active = False
        self.ds.log_action("DEACTIVATE_VOTER", admin_username, f"Deactivated voter: {voter.full_name}")
        self.ds.save_data()
        return True, f"Voter '{voter.full_name}' deactivated successfully."

    def search_voters(self, choice, term=None, station_id=None):
        results = []
        if choice == "1" and term:
            results = [v for v in self.ds.voters.values() if term.lower() in v.full_name.lower()]
        elif choice == "2" and term:
            results = [v for v in self.ds.voters.values() if term == v.voter_card_number]
        elif choice == "3" and term:
            results = [v for v in self.ds.voters.values() if term == v.national_id]
        elif choice == "4" and station_id is not None:
             results = [v for v in self.ds.voters.values() if v.station_id == station_id]
        return results

    def change_password(self, voter_id, old_pass, new_pass):
        voter = self.ds.voters.get(voter_id)
        if not voter: return False, "Voter not found."
        
        if AuthService.hash_password(old_pass) != voter.password:
            return False, "Incorrect current password."
            
        if len(new_pass) < 6:
            return False, "Password must be at least 6 characters."
            
        voter.password = AuthService.hash_password(new_pass)
        self.ds.log_action("CHANGE_PASSWORD", voter.voter_card_number, "Password changed")
        self.ds.save_data()
        return True, "Password changed successfully!"
