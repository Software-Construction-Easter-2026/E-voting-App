"""
Data layer: in-memory state and JSON persistence.

This module is the single place where all e-voting data lives (candidates,
stations, polls, voters, admins, votes, audit log). It has one job: store
and retrieve that data, and save/load it to/from a JSON file. It does not
display anything or enforce business rules; those are handled by the UI
and service layers.
"""
import json
import os
import datetime
import hashlib

from src.config.constants import DATA_FILE


class Repository:
    """
    Holds all e-voting data in memory and persists to JSON.
    Replaces the original global dicts and counters.
    """

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
        self._ensure_default_admin()

    def _ensure_default_admin(self):
        """Create default admin if none exist (first run)."""
        if not self.admins:
            self.admins[1] = {
                "id": 1,
                "username": "admin",
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "full_name": "System Administrator",
                "email": "admin@evote.com",
                "role": "super_admin",
                "created_at": str(datetime.datetime.now()),
                "is_active": True,
            }
            self.admin_id_counter = 2

    def save(self) -> tuple[bool, str]:
        """
        Persist all data to JSON file.
        Returns (success, message) for the UI to display.
        """
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
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return True, "Data saved successfully"
        except Exception as e:
            return False, f"Error saving data: {e}"

    def load(self) -> tuple[bool, str]:
        """
        Load data from JSON file if it exists.
        Returns (success, message).
        """
        try:
            if not os.path.exists(DATA_FILE):
                return True, ""
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
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
            return True, "Data loaded successfully"
        except Exception as e:
            return False, f"Error loading data: {e}"
