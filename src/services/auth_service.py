"""
Authentication and registration: login (admin/voter), voter registration.
Implemented as AuthService(BaseService) for encapsulation and OOP.
"""
import datetime
import hashlib
import random
import string

from src.config.constants import MIN_VOTER_AGE
from src.services.base_service import BaseService


class AuthService(BaseService):
    """
    Handles admin/voter login and voter registration. Encapsulates
    password hashing and voter card generation; no UI.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Return SHA-256 hex digest of password."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_voter_card_number() -> str:
        """Generate a unique 12-character voter card number."""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def try_admin_login(self, username: str, password: str) -> tuple[bool, str, object]:
        """
        Attempt admin login. Returns (success, message, admin_dict or None).
        """
        hashed = self.hash_password(password)
        for aid, admin in self.repo.admins.items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    return False, "This account has been deactivated.", None
                return True, f"Welcome, {admin['full_name']}!", admin
        return False, "Invalid credentials.", None

    def try_voter_login(self, voter_card: str, password: str) -> tuple[bool, str, object]:
        """
        Attempt voter login. Returns (success, message, voter_dict or None).
        """
        hashed = self.hash_password(password)
        for vid, voter in self.repo.voters.items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    return False, "This voter account has been deactivated.", None
                if not voter["is_verified"]:
                    return False, "not_verified", voter
                return True, f"Welcome, {voter['full_name']}!", voter
        return False, "Invalid voter card number or password.", None

    def register_voter(
        self,
        full_name: str,
        national_id: str,
        dob_str: str,
        gender: str,
        address: str,
        phone: str,
        email: str,
        password: str,
        station_id: int,
    ) -> tuple[bool, str, str]:
        """
        Register a new voter. Returns (success, message, voter_card_number).
        """
        if not full_name:
            return False, "Name cannot be empty.", ""
        if not national_id:
            return False, "National ID cannot be empty.", ""
        for v in self.repo.voters.values():
            if v["national_id"] == national_id:
                return False, "A voter with this National ID already exists.", ""
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return False, "Invalid date format.", ""
        if age < MIN_VOTER_AGE:
            return False, f"You must be at least {MIN_VOTER_AGE} years old to register.", ""
        if gender not in ["M", "F", "OTHER"]:
            return False, "Invalid gender selection.", ""
        if len(password) < 6:
            return False, "Password must be at least 6 characters.", ""
        if station_id not in self.repo.voting_stations or not self.repo.voting_stations[station_id]["is_active"]:
            return False, "Invalid station selection.", ""
        voter_card = self.generate_voter_card_number()
        vid = self.repo.voter_id_counter
        self.repo.voters[vid] = {
            "id": vid,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "address": address,
            "phone": phone,
            "email": email,
            "password": self.hash_password(password),
            "voter_card_number": voter_card,
            "station_id": station_id,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter",
        }
        self.repo.voter_id_counter += 1
        return True, "Registration successful!", voter_card
