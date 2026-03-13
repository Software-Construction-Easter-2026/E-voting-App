# Audit-logging utility.
# The single module-level `audit_logger` instance is imported wherever
# actions need to be recorded; the storage layer reads it via get_log().

import datetime


class AuditLogger:
    """Keeps an in-memory list of audit events and exposes simple access."""

    def __init__(self):
        self._log: list = []

    def log(self, action: str, user: str, details: str) -> None:
        """Append a timestamped audit entry."""
        self._log.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "user": user,
            "details": details,
        })

    def get_log(self) -> list:
        """Return the full audit log."""
        return self._log

    def set_log(self, log_data: list) -> None:
        """Restore the audit log from saved data."""
        self._log = log_data


# Shared logger instance used across the system
audit_logger = AuditLogger()