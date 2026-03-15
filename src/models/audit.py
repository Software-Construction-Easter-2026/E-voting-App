from dataclasses import dataclass

@dataclass
class AuditLogEntry:
    timestamp: str
    action: str
    user: str
    details: str
