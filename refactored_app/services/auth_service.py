"""Authentication: admin and voter login. Session is managed by this service."""

import hashlib
from typing import Optional, Tuple, Dict


def hash_password(password: str) -> str:
    """Return SHA256 hash of a password."""
    return hashlib.sha256(password.encode()).hexdigest()


# Module-level session
current_user: Optional[Dict] = None
current_role: Optional[str] = None  # "admin" | "voter"


def set_session(user: Dict, role: str) -> None:
    """Set the current session."""
    global current_user, current_role
    current_user = user
    current_role = role


def clear_session() -> None:
    """Clear the current session."""
    global current_user, current_role
    current_user = None
    current_role = None


def get_session() -> Tuple[Optional[Dict], Optional[str]]:
    """Return the current session."""
    return current_user, current_role


def _authenticate_user(user: Dict, password: str) -> bool:
    """Check if password matches stored hash."""
    return user.get("password") == hash_password(password)


def login_admin(ctx, username: str, password: str) -> Tuple[bool, Optional[str]]:
    """Authenticate an admin user."""

    for admin in ctx.admins.get_all().values():

        if admin["username"] == username and _authenticate_user(admin, password):

            if not admin.get("is_active"):
                return False, "This account has been deactivated."

            set_session(admin, "admin")
            return True, None

    return False, "Invalid credentials."


def login_voter(ctx, voter_card: str, password: str) -> Tuple[bool, Optional[str]]:
    """Authenticate a voter."""

    for voter in ctx.voters.get_all().values():

        if voter["voter_card_number"] == voter_card and _authenticate_user(voter, password):

            if not voter.get("is_active"):
                return False, "This voter account has been deactivated."

            if not voter.get("is_verified"):
                return False, "not_verified"

            set_session(voter, "voter")
            return True, None

    return False, "Invalid voter card number or password."