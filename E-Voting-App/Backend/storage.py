"""
storage.py

One class. Reads and writes JSON files.
Every module uses this — nothing else touches the file system.
"""

import json
import os


class JsonStore:
    """Reads and writes a single JSON file that holds a list of records."""

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            self._write_all_records([])

    # ── public ──────────────────────────────────────────────────────────

    def all(self) -> list[dict]:
        """Return every record in the file."""
        return self._read_all_records()

    def find(self, **field_filters) -> list[dict]:
        """Return all records where every given field matches.
           Example: store.find(status="open")
        """
        all_records = self._read_all_records()
        return [
            record for record in all_records
            if all(record.get(field_name) == expected_value
                   for field_name, expected_value in field_filters.items())
        ]

    def find_one(self, **field_filters) -> dict | None:
        """Return the first matching record, or None if none found."""
        matching_records = self.find(**field_filters)
        return matching_records[0] if matching_records else None

    def insert(self, new_record: dict) -> dict:
        """Assign a new id to the record, save it, and return it."""
        all_records = self._read_all_records()
        new_record["id"] = self._next_available_id(all_records)
        all_records.append(new_record)
        self._write_all_records(all_records)
        return new_record

    def update(self, record_id: int, field_changes: dict) -> dict | None:
        """Apply field_changes to the record matching record_id.
           Returns the updated record, or None if not found.
        """
        all_records = self._read_all_records()
        for record in all_records:
            if record["id"] == record_id:
                record.update(field_changes)
                self._write_all_records(all_records)
                return record
        return None

    def delete(self, record_id: int) -> bool:
        """Remove the record with the given id.
           Returns True if a record was deleted, False if none matched.
        """
        all_records = self._read_all_records()
        remaining_records = [r for r in all_records if r["id"] != record_id]
        record_was_found = len(remaining_records) < len(all_records)
        if record_was_found:
            self._write_all_records(remaining_records)
        return record_was_found

    # ── private ─────────────────────────────────────────────────────────

    def _read_all_records(self) -> list[dict]:
        with open(self._file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def _write_all_records(self, records: list[dict]) -> None:
        with open(self._file_path, "w", encoding="utf-8") as json_file:
            json.dump(records, json_file, indent=2, default=str)

    def _next_available_id(self, existing_records: list[dict]) -> int:
        return max((record["id"] for record in existing_records), default=0) + 1
