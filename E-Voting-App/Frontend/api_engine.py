"""
api_engine.py

A small database-ish engine for the E-Voting system.
Treats a single JSON file (database.json) as a collection of "tables"
(top-level keys). Provides an API-like interface so that no other module
touches the filesystem directly.

Tables:
    candidates, voting_stations, polls, positions,
    voters, admins, votes, audit_log

Design Principles:
    - Single Responsibility: only this module reads/writes the JSON file.
    - Open/Closed: new tables can be added without modifying existing code.
    - Encapsulation: internal data is accessed exclusively through methods.
"""

import json
import os
import datetime
from copy import deepcopy


# ── Default schema for a fresh database ──────────────────────────────────────

_DEFAULT_SCHEMA = {
    "candidates":          {},
    "candidate_id_counter": 1,
    "voting_stations":     {},
    "station_id_counter":   1,
    "polls":               {},
    "poll_id_counter":      1,
    "positions":           {},
    "position_id_counter":  1,
    "voters":              {},
    "voter_id_counter":     1,
    "admins":              {},
    "admin_id_counter":     1,
    "votes":               [],
    "audit_log":           [],
}


class DatabaseEngine:
    """
    Central data-access layer for the E-Voting application.

    Usage:
        db = DatabaseEngine("database.json")
        db.load()
        voters = db.get_all("voters")
        db.insert("voters", voter_id, voter_record)
        db.save()
    """

    def __init__(self, file_path: str = "database.json") -> None:
        self._file_path = file_path
        self._data: dict = {}

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load database from disk. Creates the file with defaults if missing."""
        if not os.path.exists(self._file_path):
            self._data = deepcopy(_DEFAULT_SCHEMA)
            self._persist()
            return
        with open(self._file_path, "r", encoding="utf-8") as json_file:
            raw = json.load(json_file)
        # Ensure integer keys for dict-tables
        self._data = {}
        for key, value in _DEFAULT_SCHEMA.items():
            if key not in raw:
                self._data[key] = deepcopy(value)
            elif isinstance(value, dict) and not key.endswith("_counter"):
                self._data[key] = {int(k): v for k, v in raw[key].items()}
            else:
                self._data[key] = raw[key]

    def save(self) -> None:
        """Persist the current in-memory data to disk."""
        self._persist()

    def _persist(self) -> None:
        with open(self._file_path, "w", encoding="utf-8") as json_file:
            json.dump(self._data, json_file, indent=2, default=str)

    # ── Generic table access (dict-based tables) ─────────────────────────

    def get_all(self, table_name: str) -> dict:
        """Return a shallow copy of all records in a dict-table."""
        self._validate_table(table_name)
        return dict(self._data[table_name])

    def get_by_id(self, table_name: str, record_id: int) -> dict | None:
        """Return a single record by its integer id, or None."""
        self._validate_table(table_name)
        return self._data[table_name].get(record_id)

    def find(self, table_name: str, **filters) -> list[dict]:
        """Return records matching ALL key=value filters."""
        self._validate_table(table_name)
        results = []
        source = self._data[table_name]
        items = source.values() if isinstance(source, dict) else source
        for record in items:
            if all(record.get(k) == v for k, v in filters.items()):
                results.append(record)
        return results

    def insert(self, table_name: str, record_id: int, record: dict) -> dict:
        """Insert a record into a dict-table under the given id."""
        self._validate_table(table_name)
        self._data[table_name][record_id] = record
        self._persist()
        return record

    def update(self, table_name: str, record_id: int, changes: dict) -> dict | None:
        """Merge *changes* into the record identified by record_id."""
        self._validate_table(table_name)
        record = self._data[table_name].get(record_id)
        if record is None:
            return None
        record.update(changes)
        self._persist()
        return record

    def delete(self, table_name: str, record_id: int) -> bool:
        """Delete a record from a dict-table. Returns True if found."""
        self._validate_table(table_name)
        if record_id in self._data[table_name]:
            del self._data[table_name][record_id]
            self._persist()
            return True
        return False

    # ── Counter helpers ───────────────────────────────────────────────────

    def get_next_id(self, table_name: str) -> int:
        """Return the current counter value for *table_name*."""
        counter_key = f"{table_name}_id_counter"
        if table_name == "voting_stations":
            counter_key = "station_id_counter"
        elif table_name == "candidates":
            counter_key = "candidate_id_counter"
        return self._data.get(counter_key, 1)

    def increment_counter(self, table_name: str) -> None:
        """Advance the id counter for *table_name* by one and persist."""
        counter_key = f"{table_name}_id_counter"
        if table_name == "voting_stations":
            counter_key = "station_id_counter"
        elif table_name == "candidates":
            counter_key = "candidate_id_counter"
        self._data[counter_key] = self._data.get(counter_key, 1) + 1
        self._persist()

    # ── List-based table access (votes, audit_log) ────────────────────────

    def get_list(self, list_name: str) -> list:
        """Return a shallow copy of a list-table (e.g. votes, audit_log)."""
        return list(self._data.get(list_name, []))

    def append_to_list(self, list_name: str, record: dict) -> None:
        """Append a record to a list-table and persist."""
        if list_name not in self._data:
            self._data[list_name] = []
        self._data[list_name].append(record)
        self._persist()

    def filter_list(self, list_name: str, **filters) -> list[dict]:
        """Return items from a list-table matching all filters."""
        results = []
        for item in self._data.get(list_name, []):
            if all(item.get(k) == v for k, v in filters.items()):
                results.append(item)
        return results

    def replace_list(self, list_name: str, new_list: list) -> None:
        """Replace an entire list-table (e.g. after filtering out deleted votes)."""
        self._data[list_name] = new_list
        self._persist()

    # ── Audit log convenience ─────────────────────────────────────────────

    def log_action(self, action: str, user: str, details: str) -> None:
        """Append an entry to the audit_log list."""
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        }
        self.append_to_list("audit_log", entry)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _validate_table(self, table_name: str) -> None:
        """Raise ValueError if the table is unknown."""
        if table_name not in self._data:
            raise ValueError(
                f"Unknown table '{table_name}'. "
                f"Available: {[k for k in self._data if not k.endswith('_counter')]}"
            )
