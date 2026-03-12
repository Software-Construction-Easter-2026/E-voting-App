"""Audit logging."""

import datetime


def log_action(ctx, action: str, user: str, details: str):
    ctx.audit.append({
        "timestamp": str(datetime.datetime.now()),
        "action": action,
        "user": user,
        "details": details,
    })
