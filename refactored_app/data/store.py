"""In-memory data store and JSON persistence.
Single source of truth for all entities.
"""

import datetime
import hashlib
import json
import os


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class DataStore:
    """Stores all entities and handles JSON persistence."""

    DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "evoting_data.json")

    def __init__(self):
        self.candidates = {}
        self.candidate_id_counter = 1

        self.voting_stations = {}
        self.station_id_counter = 1

        self.polls = {}
        self.poll_id_counter = 1

        self.positions = {}
        self.position_id_counter = 1

        self.voters = {}
        self.voter_id_counter = 1

        self.admins = {}
        self.admin_id_counter = 1

        self.votes = []
        self.audit_log = []

    def _ensure_default_admin(self):
        """Ensure default super admin exists."""
        if 1 not in self.admins:
            self.admins[1] = {
                "id": 1,
                "username": "admin",
                "password": _hash_password("admin123"),
                "full_name": "System Administrator",
                "email": "admin@evote.com",
                "role": "super_admin",
                "created_at": str(datetime.datetime.now()),
                "is_active": True,
            }
            self.admin_id_counter = 2

    def load(self):
        """Load system data from JSON."""
        try:
            if not os.path.exists(self.DATA_FILE):
                self._ensure_default_admin()
                return True, "no_file"

            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._load_entities(data)

            self._ensure_default_admin()
            return True, None

        except Exception as e:
            return False, str(e)

    def _load_entities(self, data):
        """Populate datastore fields from loaded JSON."""
        self.candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
        self.candidate_id_counter = data.get("candidate_id_counter", 1)

        self.voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
        self.station_id_counter = data.get("station_id_counter", 1)

        self.polls = {int(k): v for k, v in data.get("polls", {}).items()}
        self.poll_id_counter = data.get("poll_id_counter", 1)

        self.positions = {int(k): v for k, v in data.get("positions", {}).items()}
        self.position_id_counter = data.get("position_id_counter", 1)

        self.voters = {int(k): v for k, v in data.get("voters", {}).items()}
        self.voter_id_counter = data.get("voter_id_counter", 1)

        self.admins = {int(k): v for k, v in data.get("admins", {}).items()}
        self.admin_id_counter = data.get("admin_id_counter", 1)

        self.votes = data.get("votes", [])
        self.audit_log = data.get("audit_log", [])

    def save(self):
        """Save system data to JSON."""
        data = {
            "candidates": self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": self.voting_stations,
            "station_id_counter": self.station_id_counter,
            "polls": self.polls,
            "poll_id_counter": self.poll_id_counter,
            "positions": self.positions,
            "position_id_counter": self.position_id_counter,
            "voters": self.voters,
            "voter_id_counter": self.voter_id_counter,
            "admins": self.admins,
            "admin_id_counter": self.admin_id_counter,
            "votes": self.votes,
            "audit_log": self.audit_log,
        }

        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return True, None

        except Exception as e:
            return False, str(e)