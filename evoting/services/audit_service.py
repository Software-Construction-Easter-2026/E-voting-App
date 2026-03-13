import datetime


class AuditService:
    def __init__(self, repository):
        self._repo = repository

    def log(self, action, user, details):
        self._repo.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        })
