import hashlib
import random
import string
import datetime

from evoting.core.constants import MIN_VOTER_AGE


class AuthService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service
        self.current_user = None
        self.current_role = None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_voter_card_number(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def login_admin(self, username, password):
        hashed = self.hash_password(password)
        for aid, admin in self._repo.admins.items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    return False, "deactivated"
                self.current_user = admin
                self.current_role = "admin"
                self._audit.log("LOGIN", username, "Admin login successful")
                return True, admin
        self._audit.log("LOGIN_FAILED", username, "Invalid admin credentials")
        return False, "invalid"

    def login_voter(self, voter_card, password):
        hashed = self.hash_password(password)
        for vid, voter in self._repo.voters.items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    return False, "deactivated"
                if not voter["is_verified"]:
                    return False, "unverified"
                self.current_user = voter
                self.current_role = "voter"
                self._audit.log("LOGIN", voter_card, "Voter login successful")
                return True, voter
        self._audit.log("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        return False, "invalid"

    def logout(self):
        if self.current_user and self.current_role == "admin":
            self._audit.log("LOGOUT", self.current_user["username"], "Admin logged out")
        elif self.current_user and self.current_role == "voter":
            self._audit.log("LOGOUT", self.current_user["voter_card_number"], "Voter logged out")
        self.current_user = None
        self.current_role = None

    def register_voter(self, data):
        for v in self._repo.voters.values():
            if v["national_id"] == data["national_id"]:
                return False, "duplicate_national_id"
        try:
            dob = datetime.datetime.strptime(data["dob_str"], "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return False, "invalid_date"
        if age < MIN_VOTER_AGE:
            return False, "underage"
        if data["gender"].upper() not in ("M", "F", "OTHER"):
            return False, "invalid_gender"
        if len(data["password"]) < 6:
            return False, "short_password"
        if data["password"] != data["confirm_password"]:
            return False, "password_mismatch"
        station_id = data.get("station_id")
        if not station_id or station_id not in self._repo.voting_stations:
            return False, "invalid_station"
        station = self._repo.voting_stations[station_id]
        if not station.get("is_active", True):
            return False, "invalid_station"
        voter_card = self.generate_voter_card_number()
        vid = self._repo.voter_id_counter
        self._repo.voters[vid] = {
            "id": vid,
            "full_name": data["full_name"],
            "national_id": data["national_id"],
            "date_of_birth": data["dob_str"],
            "age": age,
            "gender": data["gender"].upper(),
            "address": data["address"],
            "phone": data["phone"],
            "email": data["email"],
            "password": self.hash_password(data["password"]),
            "voter_card_number": voter_card,
            "station_id": station_id,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter",
        }
        self._repo.voter_id_counter += 1
        self._audit.log("REGISTER", data["full_name"], f"New voter registered with card: {voter_card}")
        return True, {"voter_card_number": voter_card}
