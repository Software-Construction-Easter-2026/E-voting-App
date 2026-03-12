"""Candidate CRUD and search. Eligibility: age, education, no criminal record."""

import datetime

from models.constants import (
    MIN_CANDIDATE_AGE,
    MAX_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
)

from services.auth_service import current_user
from services import validation


def create(ctx, data: dict) -> tuple[bool, str]:
    """Create candidate. Returns (True, id) or (False, error_message)."""

    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        return False, "Name cannot be empty."

    national_id = (data.get("national_id") or "").strip()
    if not national_id:
        return False, "National ID cannot be empty."

    # Prevent duplicate national ID
    for c in ctx.candidates.get_all().values():
        if c["national_id"] == national_id:
            return False, "A candidate with this National ID already exists."

    # Validate DOB
    dob_str = (data.get("date_of_birth") or "").strip()
    ok, err = validation.validate_candidate_dob(dob_str)
    if not ok:
        return False, err

    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    age = (datetime.datetime.now() - dob).days // 365

    # Education constraint
    education = data.get("education")
    if education not in REQUIRED_EDUCATION_LEVELS:
        return False, "Invalid education level."

    # Criminal record constraint
    if data.get("has_criminal_record") is True:
        return False, "criminal_record"

    # Email validation
    email = (data.get("email") or "").strip()
    if email and not validation.is_valid_email(email):
        return False, "Invalid email address (e.g. name@example.com)."

    # Phone validation
    phone = (data.get("phone") or "").strip()
    ok, err = validation.validate_phone(phone)
    if not ok:
        return False, err
    phone = validation.normalize_phone(phone) if phone else ""

    cid = ctx.candidates.next_id()

    candidate = {
        "id": cid,
        "full_name": full_name,
        "national_id": national_id,
        "date_of_birth": dob_str,
        "age": age,
        "gender": data.get("gender", ""),
        "education": education,
        "party": data.get("party", ""),
        "manifesto": data.get("manifesto", ""),
        "address": data.get("address", ""),
        "phone": phone,
        "email": email,
        "has_criminal_record": False,
        "years_experience": data.get("years_experience", 0),
        "is_active": True,
        "is_approved": True,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_user["username"] if current_user else "",
    }

    ctx.candidates.add(cid, candidate)

    return True, str(cid)


def get_all(ctx):
    return ctx.candidates.get_all()


def get_by_id(ctx, cid: int):
    return ctx.candidates.get_by_id(cid)


def update(ctx, cid: int, updates: dict) -> tuple[bool, str]:
    """Update candidate details."""

    candidate = ctx.candidates.get_by_id(cid)
    if not candidate:
        return False, "Candidate not found."

    if "phone" in updates and updates["phone"] is not None:
        phone = updates["phone"].strip()
        if phone and not validation.is_valid_phone(phone):
            return False, "Phone must start with 07 and have 10 digits (e.g. 0712345678)."
        candidate["phone"] = validation.normalize_phone(phone) if phone else ""

    if "email" in updates and updates["email"] is not None:
        email = updates["email"].strip()
        if email and not validation.is_valid_email(email):
            return False, "Invalid email address (e.g. name@example.com)."
        candidate["email"] = email

    for key in ("full_name", "party", "manifesto", "address"):
        if key in updates and updates[key] is not None:
            candidate[key] = updates[key]

    if "years_experience" in updates and updates["years_experience"] is not None:
        try:
            candidate["years_experience"] = int(updates["years_experience"])
        except (ValueError, TypeError):
            pass

    return True, ""


def can_delete(ctx, cid: int) -> tuple[bool, str]:
    """Check if candidate can be deleted (not in active poll)."""

    polls = ctx.polls.get_all()

    for poll in polls.values():
        if poll.get("status") == "open":
            for pos in poll.get("positions", []):
                if cid in pos.get("candidate_ids", []):
                    return False, f"Cannot delete - candidate is in active poll: {poll['title']}"

    return True, ""


def deactivate(ctx, cid: int) -> bool:
    """Deactivate candidate."""

    candidate = ctx.candidates.get_by_id(cid)

    if not candidate:
        return False

    candidate["is_active"] = False
    return True


def search_by_name(ctx, term: str):
    term = term.lower()
    return [
        c for c in ctx.candidates.get_all().values()
        if term in c["full_name"].lower()
    ]


def search_by_party(ctx, term: str):
    term = term.lower()
    return [
        c for c in ctx.candidates.get_all().values()
        if term in c["party"].lower()
    ]


def search_by_education(ctx, education: str):
    return [
        c for c in ctx.candidates.get_all().values()
        if c["education"] == education
    ]


def search_by_age_range(ctx, min_age: int, max_age: int):
    return [
        c for c in ctx.candidates.get_all().values()
        if min_age <= c["age"] <= max_age
    ]