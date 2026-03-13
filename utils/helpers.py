# Pure utility functions with no side-effects.
# Any module in the project may import from here freely.

import datetime
import hashlib
import random
import string


def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of a plain-text password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number() -> str:
    """Generate a random 12-character alphanumeric voter card number."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def calculate_age(dob_str: str) -> int:
    """
    Parse a 'YYYY-MM-DD' date string and return the person's age in whole years.
    Raises ValueError if the format is incorrect (caller should handle it).
    """
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    return (datetime.datetime.now() - dob).days // 365


def current_timestamp() -> str:
    """Return the current date-time as a readable string."""
    return str(datetime.datetime.now())
