import json
import os
import hashlib
from datetime import datetime
from src.models.user import Admin, Voter
from src.models.domain import Candidate, Poll, Position, Station
from src.models.vote import Vote
from src.models.audit import AuditLogEntry

class DataStore:
    def __init__(self, file_path="evoting_data.json"):
        self.file_path = file_path
        self.candidates: dict[int, Candidate] = {}
        self.candidate_id_counter = 1
        self.voting_stations: dict[int, Station] = {}
        self.station_id_counter = 1
        self.polls: dict[int, Poll] = {}
        self.poll_id_counter = 1
        self.positions: dict[int, Position] = {}
        self.position_id_counter = 1
        self.voters: dict[int, Voter] = {}
        self.voter_id_counter = 1
        self.admins: dict[int, Admin] = {}
        self.admin_id_counter = 1
        self.votes: list[Vote] = []
        self.audit_log: list[AuditLogEntry] = []
        
        # Seed default admin if missing
        self._seed_default_admin()

    def _seed_default_admin(self):
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        self.admins[1] = Admin(
            id=1, username="admin", password=hashed, full_name="System Administrator",
            email="admin@evote.com", role="super_admin", is_active=True,
            created_at=str(datetime.now())
        )
        self.admin_id_counter = 2

    def load_data(self) -> bool:
        if not os.path.exists(self.file_path):
            return False
            
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                
            self.candidate_id_counter = data.get("candidate_id_counter", 1)
            self.station_id_counter = data.get("station_id_counter", 1)
            self.poll_id_counter = data.get("poll_id_counter", 1)
            self.position_id_counter = data.get("position_id_counter", 1)
            self.voter_id_counter = data.get("voter_id_counter", 1)
            self.admin_id_counter = data.get("admin_id_counter", 1)
            
            # Load admins
            self.admins = {}
            for k, v in data.get("admins", {}).items():
                self.admins[int(k)] = Admin(**v)
                
            # Load voters
            self.voters = {}
            for k, v in data.get("voters", {}).items():
                self.voters[int(k)] = Voter(**v)
                
            # Load candidates
            self.candidates = {}
            for k, v in data.get("candidates", {}).items():
                self.candidates[int(k)] = Candidate(**v)
                
            # Load stations
            self.voting_stations = {}
            for k, v in data.get("voting_stations", {}).items():
                self.voting_stations[int(k)] = Station(**v)
                
            # Load positions
            self.positions = {}
            for k, v in data.get("positions", {}).items():
                self.positions[int(k)] = Position(**v)
                
            # Load polls
            self.polls = {}
            for k, v in data.get("polls", {}).items():
                self.polls[int(k)] = Poll(**v)
                
            # Load votes
            self.votes = [Vote(**v) for v in data.get("votes", [])]
            
            # Load audit log
            self.audit_log = [AuditLogEntry(**v) for v in data.get("audit_log", [])]
            
            return True
        except Exception as e:
            return False

    def save_data(self) -> bool:
        data = {
            "candidate_id_counter": self.candidate_id_counter,
            "station_id_counter": self.station_id_counter,
            "poll_id_counter": self.poll_id_counter,
            "position_id_counter": self.position_id_counter,
            "voter_id_counter": self.voter_id_counter,
            "admin_id_counter": self.admin_id_counter,
            
            "admins": {str(k): vars(v) for k, v in self.admins.items()},
            "voters": {str(k): vars(v) for k, v in self.voters.items()},
            "candidates": {str(k): vars(v) for k, v in self.candidates.items()},
            "voting_stations": {str(k): vars(v) for k, v in self.voting_stations.items()},
            "positions": {str(k): vars(v) for k, v in self.positions.items()},
            "polls": {str(k): vars(v) for k, v in self.polls.items()},
            "votes": [vars(v) for v in self.votes],
            "audit_log": [vars(a) for a in self.audit_log]
        }
        
        try:
            # write atomicly
            tmp_path = self.file_path + ".tmp"
            with open(tmp_path, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.file_path)
            return True
        except Exception as e:
            return False

    def log_action(self, action: str, user: str, details: str):
        entry = AuditLogEntry(
            timestamp=str(datetime.now()),
            action=action,
            user=user,
            details=details
        )
        self.audit_log.append(entry)
