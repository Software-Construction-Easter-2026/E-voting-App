"""
audits.py

Audit log module.
Records every significant action taken in the system.
Data is stored in data/audits.json.

Every other module calls LogAuditEntry after completing an operation.
The audit log is append-only — entries are never edited or deleted.

Classes:
    AuditStore          — shared JsonStore instance for this module
    LogAuditEntry       — records one action to the audit log
    GetAllAuditEntries  — returns every entry (full history)
    GetAuditEntriesByAdmin   — returns all entries made by a specific admin
    GetAuditEntriesByAction  — returns all entries matching a specific action name
    GetRecentAuditEntries    — returns the N most recent entries
"""

import datetime
from Backend.storage import JsonStore


# ── Shared store ──────────────────────────────────────────────────────────────

class AuditStore:
    """Single access point to the audits JSON file for all audit operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/audits.json")
        return cls._instance


# ── Valid action names ────────────────────────────────────────────────────────
# Keeping action names as constants prevents typos across modules.

class AuditAction:
    # Poll actions
    POLL_CREATED            = "POLL_CREATED"
    POLL_UPDATED            = "POLL_UPDATED"
    POLL_DELETED            = "POLL_DELETED"
    POLL_OPENED             = "POLL_OPENED"
    POLL_CLOSED             = "POLL_CLOSED"
    CANDIDATES_ASSIGNED     = "CANDIDATES_ASSIGNED"

    # Voter actions
    VOTER_VERIFIED          = "VOTER_VERIFIED"
    ALL_VOTERS_VERIFIED     = "ALL_VOTERS_VERIFIED"
    VOTER_DEACTIVATED       = "VOTER_DEACTIVATED"

    # Admin actions
    ADMIN_CREATED           = "ADMIN_CREATED"
    ADMIN_DEACTIVATED       = "ADMIN_DEACTIVATED"
    ADMIN_LOGIN             = "ADMIN_LOGIN"
    ADMIN_LOGIN_FAILED      = "ADMIN_LOGIN_FAILED"


# ── Operations ────────────────────────────────────────────────────────────────

class LogAuditEntry:
    """
    Records one action to the audit log.

    Usage:
        LogAuditEntry().execute(
            action_name  = AuditAction.POLL_CREATED,
            performed_by = current_admin["username"],
            details      = f"Created poll '{poll['title']}' (id={poll['id']})",
        )
    """

    def __init__(self) -> None:
        self._audit_store = AuditStore.get()

    def execute(self, action_name: str, performed_by: str, details: str) -> dict:
        audit_entry = {
            "action_name":  action_name,
            "performed_by": performed_by,
            "details":      details,
            "recorded_at":  str(datetime.datetime.now()),
        }
        return self._audit_store.insert(audit_entry)


class GetAllAuditEntries:
    """Returns every audit entry in chronological order (oldest first)."""

    def __init__(self) -> None:
        self._audit_store = AuditStore.get()

    def execute(self) -> list[dict]:
        return self._audit_store.all()


class GetAuditEntriesByAdmin:
    """Returns all audit entries created by a specific admin username."""

    def __init__(self) -> None:
        self._audit_store = AuditStore.get()

    def execute(self, admin_username: str) -> list[dict]:
        return self._audit_store.find(performed_by=admin_username)


class GetAuditEntriesByAction:
    """Returns all audit entries that match a specific action name.
       Use AuditAction constants as the action_name argument.
       Example: GetAuditEntriesByAction().execute(AuditAction.POLL_CREATED)
    """

    def __init__(self) -> None:
        self._audit_store = AuditStore.get()

    def execute(self, action_name: str) -> list[dict]:
        return self._audit_store.find(action_name=action_name)


class GetRecentAuditEntries:
    """Returns the N most recent audit entries (newest first)."""

    DEFAULT_NUMBER_OF_ENTRIES = 20

    def __init__(self) -> None:
        self._audit_store = AuditStore.get()

    def execute(self, number_of_entries: int = DEFAULT_NUMBER_OF_ENTRIES) -> list[dict]:
        all_entries = self._audit_store.all()
        entries_newest_first = list(reversed(all_entries))
        return entries_newest_first[:number_of_entries]
