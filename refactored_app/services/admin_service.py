"""Admin account creation and deactivation."""

import datetime
from services.auth_service import current_user, hash_password
from services import validation


def can_create_admin(ctx) -> bool:
    return current_user and current_user.get("role") == "super_admin"


def can_deactivate_admin(ctx) -> bool:
    return current_user and current_user.get("role") == "super_admin"


def create_admin(ctx, data: dict) -> tuple[bool, str]:
    username = (data.get("username") or "").strip()
    if not username:
        return False, "Username cannot be empty."
    for a in ctx.admins.get_all().values():
        if a.get("username") == username:
            return False, "Username already exists."
    password = data.get("password", "")
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    role = data.get("role", "")
    if role not in ("super_admin", "election_officer", "station_manager", "auditor"):
        return False, "Invalid role."
    email = (data.get("email") or "").strip()
    if email and not validation.is_valid_email(email):
        return False, "Invalid email address (e.g. name@example.com)."
    aid = ctx.admins.next_id()
    admin = {
        "id": aid,
        "username": username,
        "password": hash_password(password),
        "full_name": data.get("full_name", ""),
        "email": email,
        "role": role,
        "created_at": str(datetime.datetime.now()),
        "is_active": True,
    }
    ctx.admins.add(aid, admin)
    return True, str(aid)


def get_all(ctx):
    return ctx.admins.get_all()


def get_by_id(ctx, aid: int):
    return ctx.admins.get_by_id(aid)


def deactivate(ctx, aid: int) -> tuple[bool, str]:
    a = ctx.admins.get_by_id(aid)
    if not a:
        return False, "Admin not found."
    if current_user and a.get("id") == current_user.get("id"):
        return False, "Cannot deactivate your own account."
    a["is_active"] = False
    return True, ""
