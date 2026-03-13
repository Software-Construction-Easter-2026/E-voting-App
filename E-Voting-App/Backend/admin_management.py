"""
admins.py

Admin account management module.
One class per operation. Data is stored in data/admins.json.

Classes:
    AdminStore        — shared JsonStore instance for this module
    AuthenticateAdmin — checks username + password, returns admin or raises
    CreateAdmin       — creates a new admin account (super_admin only)
    GetAllAdmins      — returns every admin account
    GetAdmin          — returns one admin by id
    DeactivateAdmin   — deactivates an admin account (super_admin only, not self)
"""

import datetime
import hashlib
from Backend.storage import JsonStore


# ── Shared store ──────────────────────────────────────────────────────────────

class AdminStore:
    """Single access point to the admins JSON file for all admin operations."""
    _instance: JsonStore | None = None

    @classmethod
    def get(cls) -> JsonStore:
        if cls._instance is None:
            cls._instance = JsonStore("data/admins.json")
        return cls._instance


# ── Constants ─────────────────────────────────────────────────────────────────

VALID_ADMIN_ROLES    = {"super_admin", "election_officer", "station_manager", "auditor"}
MINIMUM_PASSWORD_LENGTH = 6


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain_text_password: str) -> str:
    return hashlib.sha256(plain_text_password.encode()).hexdigest()


# ── Invariants ────────────────────────────────────────────────────────────────

def _require_requesting_admin_is_super_admin(requesting_admin: dict) -> None:
    if requesting_admin["role"] != "super_admin":
        raise PermissionError("Only super admins can perform this action.")


def _require_valid_admin_role(role: str) -> None:
    if role not in VALID_ADMIN_ROLES:
        raise ValueError(
            f"Invalid role '{role}'. "
            f"Valid roles are: {', '.join(sorted(VALID_ADMIN_ROLES))}"
        )


def _require_password_is_strong_enough(plain_text_password: str) -> None:
    if len(plain_text_password) < MINIMUM_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters."
        )


def _require_username_is_not_already_taken(username: str, admin_store: JsonStore) -> None:
    if admin_store.find_one(username=username) is not None:
        raise ValueError(f"Username '{username}' is already taken.")


def _require_target_is_not_the_requesting_admin(target_admin_id: int, requesting_admin: dict) -> None:
    if target_admin_id == requesting_admin["id"]:
        raise ValueError("You cannot deactivate your own account.")


def _require_admin_is_currently_active(admin: dict) -> None:
    if not admin["is_active"]:
        raise ValueError(f"Admin '{admin['username']}' is already inactive.")


# ── Operations ────────────────────────────────────────────────────────────────

class AuthenticateAdmin:
    """
    Verifies a username and password combination.
    Returns the admin record on success, raises ValueError on failure.
    """

    def __init__(self) -> None:
        self._admin_store = AdminStore.get()

    def execute(self, username: str, plain_text_password: str) -> dict:
        matched_admin = self._admin_store.find_one(username=username)
        credentials_are_invalid = (
            matched_admin is None
            or not matched_admin["is_active"]
            or matched_admin["password_hash"] != hash_password(plain_text_password)
        )
        if credentials_are_invalid:
            raise ValueError("Invalid credentials or account inactive.")
        return matched_admin


class GetAllAdmins:
    """Returns every admin account."""

    def __init__(self) -> None:
        self._admin_store = AdminStore.get()

    def execute(self) -> list[dict]:
        return self._admin_store.all()


class GetAdmin:
    """Returns a single admin by id, or raises ValueError if not found."""

    def __init__(self) -> None:
        self._admin_store = AdminStore.get()

    def execute(self, admin_id: int) -> dict:
        matching_admin = self._admin_store.find_one(id=admin_id)
        if matching_admin is None:
            raise ValueError(f"Admin {admin_id} not found.")
        return matching_admin


class CreateAdmin:
    """
    Creates a new admin account.
    Only a super_admin may create other admins.
    """

    def __init__(self, requesting_admin: dict) -> None:
        self._admin_store       = AdminStore.get()
        self._requesting_admin  = requesting_admin

    def execute(
        self,
        username:           str,
        plain_text_password: str,
        full_name:          str,
        email:              str,
        role:               str,
    ) -> dict:
        _require_requesting_admin_is_super_admin(self._requesting_admin)
        _require_valid_admin_role(role)
        _require_password_is_strong_enough(plain_text_password)
        _require_username_is_not_already_taken(username, self._admin_store)

        if not username:
            raise ValueError("Username cannot be empty.")

        new_admin_record = {
            "username":      username,
            "password_hash": hash_password(plain_text_password),
            "full_name":     full_name,
            "email":         email,
            "role":          role,
            "is_active":     True,
            "created_at":    str(datetime.datetime.now()),
        }
        return self._admin_store.insert(new_admin_record)


class DeactivateAdmin:
    """
    Deactivates an admin account.
    Only a super_admin may do this, and they may not deactivate themselves.
    """

    def __init__(self, requesting_admin: dict) -> None:
        self._admin_store      = AdminStore.get()
        self._requesting_admin = requesting_admin

    def execute(self, target_admin_id: int) -> dict:
        _require_requesting_admin_is_super_admin(self._requesting_admin)
        _require_target_is_not_the_requesting_admin(target_admin_id, self._requesting_admin)

        target_admin = GetAdmin().execute(target_admin_id)
        _require_admin_is_currently_active(target_admin)

        return self._admin_store.update(target_admin_id, {"is_active": False})
