"""
Admin account management: create (super_admin only), view, deactivate.
"""
import datetime
import hashlib

from src.data.repository import Repository


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin(
    repo: Repository,
    current_username: str,
    username: str,
    full_name: str,
    email: str,
    password: str,
    role: str,
) -> tuple[bool, str]:
    """Create admin. Only super_admin can create. Returns (success, message)."""
    if not username:
        return False, "Username cannot be empty."
    for a in repo.admins.values():
        if a["username"] == username:
            return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if role not in ("super_admin", "election_officer", "station_manager", "auditor"):
        return False, "Invalid role."
    aid = repo.admin_id_counter
    repo.admins[aid] = {
        "id": aid,
        "username": username,
        "password": hash_password(password),
        "full_name": full_name,
        "email": email,
        "role": role,
        "created_at": str(datetime.datetime.now()),
        "is_active": True,
    }
    repo.admin_id_counter += 1
    return True, f"Admin '{username}' created with role: {role}"


def deactivate_admin(
    repo: Repository,
    aid: int,
    current_user_id: int,
    current_username: str,
) -> tuple[bool, str]:
    """Deactivate admin. Cannot deactivate self. Only super_admin. Returns (success, message)."""
    if aid not in repo.admins:
        return False, "Admin not found."
    if aid == current_user_id:
        return False, "Cannot deactivate your own account."
    repo.admins[aid]["is_active"] = False
    return True, "Admin deactivated."
