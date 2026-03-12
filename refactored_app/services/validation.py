"""Input validation: dates (YYYY-MM-DD), phone (07 + 10 digits), email."""

import datetime
import re

from models.constants import (
    MIN_VOTER_AGE,
    MIN_CANDIDATE_AGE,
    MAX_CANDIDATE_AGE,
)

DATE_FORMAT = "%Y-%m-%d"

PHONE_PATTERN = re.compile(r"^07\d{8}$")

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


def is_non_empty(value: str) -> bool:
    return bool((value or "").strip())


def _parse_date(value: str):
    """Parse YYYY-MM-DD date safely."""
    return datetime.datetime.strptime(value, DATE_FORMAT)


def _calculate_age(date_str: str) -> int:
    """Return age in years from a YYYY-MM-DD date string."""
    dob = _parse_date(date_str)
    return (datetime.datetime.now() - dob).days // 365


def validate_date(value: str, allow_future: bool = False) -> tuple[bool, str]:
    """
    Validate YYYY-MM-DD date format.
    Optionally reject future dates.
    """
    value = (value or "").strip()

    if not value:
        return False, "Date is required."

    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        return False, "Invalid date format. Use YYYY-MM-DD."

    try:
        dt = _parse_date(value)
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."

    if not allow_future and dt.date() > datetime.date.today():
        return False, "Date cannot be in the future."

    return True, ""


def validate_date_of_birth(value: str) -> tuple[bool, str]:
    """DOB must be valid and not in the future."""
    return validate_date(value, allow_future=False)


def validate_voter_dob(value: str) -> tuple[bool, str]:
    """Validate voter age constraint."""
    ok, err = validate_date_of_birth(value)
    if not ok:
        return False, err

    age = _calculate_age(value)

    if age < MIN_VOTER_AGE:
        return False, f"You must be at least {MIN_VOTER_AGE} years old to register."

    return True, ""


def validate_candidate_dob(value: str) -> tuple[bool, str]:
    """Validate candidate age constraints."""
    ok, err = validate_date_of_birth(value)
    if not ok:
        return False, err

    age = _calculate_age(value)

    if age < MIN_CANDIDATE_AGE:
        return False, f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"

    if age > MAX_CANDIDATE_AGE:
        return False, f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"

    return True, ""


def required_non_empty(value: str, field_name: str = "This field") -> tuple[bool, str]:
    """Required non-empty string."""
    if not (value or "").strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """Validate required email address."""
    email = (email or "").strip()

    if not email:
        return False, "Email is required."

    if not EMAIL_PATTERN.match(email):
        return False, "Invalid email address (e.g. name@example.com)."

    return True, ""


def is_valid_email(email: str) -> bool:
    """Boolean version for optional email fields."""
    email = (email or "").strip()

    if not email:
        return True

    return bool(EMAIL_PATTERN.match(email))


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to digits starting with 07."""
    phone = (phone or "").strip()

    phone = re.sub(r"[\s\-]", "", phone)

    if phone.startswith("+256"):
        phone = "0" + phone[4:]

    return phone


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate required phone number."""
    normalized = normalize_phone(phone)

    if not normalized:
        return False, "Phone number is required."

    if not PHONE_PATTERN.match(normalized):
        return False, "Phone must start with 07 and have 10 digits (e.g. 0712345678)."

    return True, ""


def is_valid_phone(phone: str) -> bool:
    """Boolean version for optional phone numbers."""
    normalized = normalize_phone(phone)

    if not normalized:
        return True

    return bool(PHONE_PATTERN.match(normalized))


def is_numeric(value: str) -> bool:
    return bool(value) and value.isdigit()


def optional_email(value: str) -> tuple[bool, str]:
    """Optional email validation."""
    value = (value or "").strip()

    if not value:
        return True, ""

    if not EMAIL_PATTERN.match(value):
        return False, "Invalid email address (e.g. name@example.com)."

    return True, ""


def optional_phone(value: str) -> tuple[bool, str]:
    """Optional phone validation."""
    normalized = normalize_phone(value)

    if not normalized:
        return True, ""

    if not PHONE_PATTERN.match(normalized):
        return False, "Phone must start with 07 and have 10 digits (e.g. 0712345678)."

    return True, ""