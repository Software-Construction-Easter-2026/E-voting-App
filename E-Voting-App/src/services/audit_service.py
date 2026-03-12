"""
Audit logging: record actions and filter entries for display.
Implemented as AuditService(BaseService) for encapsulation and OOP.
"""
import datetime

from src.services.base_service import BaseService


class AuditService(BaseService):
    """
    Records and retrieves audit log entries. No UI; callers use returned data.
    """

    def log_action(self, action: str, user: str, details: str) -> None:
        """Append an audit entry."""
        self.repo.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        })

    def get_audit_entries(self, filter_choice: str, filter_value: str = None) -> list:
        """
        Return list of audit entries for display.
        filter_choice: "1" last 20, "2" all, "3" by action type, "4" by user.
        """
        entries = self.repo.audit_log
        if filter_choice == "1":
            entries = self.repo.audit_log[-20:]
        elif filter_choice == "3" and filter_value:
            entries = [e for e in self.repo.audit_log if e["action"] == filter_value]
        elif filter_choice == "4" and filter_value:
            entries = [e for e in self.repo.audit_log if filter_value.lower() in e["user"].lower()]
        return entries

    def get_action_types(self) -> list:
        """Return unique action types for filter menu."""
        return list(set(e["action"] for e in self.repo.audit_log))


# Backward compatibility: module-level functions for code that passes repo explicitly
def log_action(repo, action: str, user: str, details: str) -> None:
    AuditService(repo).log_action(action, user, details)


def get_audit_entries(repo, filter_choice: str, filter_value: str = None) -> list:
    return AuditService(repo).get_audit_entries(filter_choice, filter_value)


def get_action_types(repo) -> list:
    return AuditService(repo).get_action_types()
