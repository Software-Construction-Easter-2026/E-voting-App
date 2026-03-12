"""Voter registration, verification, deactivation, search."""

import datetime
import random
import string

from models.constants import MIN_VOTER_AGE
from services.auth_service import hash_password
from services import validation


def generate_voter_card_number() -> str:
    """Generate a random 12-character voter card."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def register(ctx, data: dict) -> tuple[bool, str]:
    """Register a voter. Returns (True, voter_card) or (False, error_message)."""

    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        return False, "Name cannot be empty."

    national_id = (data.get("national_id") or "").strip()
    if not national_id:
        return False, "National ID cannot be empty."

    # Prevent duplicate national ID
    for voter in ctx.voters.get_all().values():
        if voter.get("national_id") == national_id:
            return False, "A voter with this National ID already exists."

    # Validate date of birth
    dob_str = (data.get("date_of_birth") or "").strip()
    ok, err = validation.validate_voter_dob(dob_str)
    if not ok:
        return False, err

    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    age = (datetime.datetime.now() - dob).days // 365

    # Gender constraint
    gender = (data.get("gender") or "").upper()
    if gender not in ("M", "F", "OTHER"):
        return False, "Invalid gender selection."

    # Email validation
    email = (data.get("email") or "").strip()
    if email and not validation.is_valid_email(email):
        return False, "Invalid email address (e.g. name@example.com)."

    # Phone validation
    phone = (data.get("phone") or "").strip()

    ok, err = validation.validate_phone(phone)
    if not ok:
     return False, err

    phone = validation.normalize_phone(phone)

    # Password validation
    password = data.get("password") or ""
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != data.get("confirm_password"):
        return False, "Passwords do not match."

    # Station validation
    station_id = data.get("station_id")
    if station_id is None:
        return False, "No voting stations available. Contact admin."

    station = ctx.stations.get_by_id(station_id)
    if not station or not station.get("is_active"):
        return False, "Invalid station selection."

    # Generate voter record
    voter_card = generate_voter_card_number()
    vid = ctx.voters.next_id()

    voter = {
        "id": vid,
        "full_name": full_name,
        "national_id": national_id,
        "date_of_birth": dob_str,
        "age": age,
        "gender": gender,
        "address": data.get("address", ""),
        "phone": phone,
        "email": email,
        "password": hash_password(password),
        "voter_card_number": voter_card,
        "station_id": station_id,
        "is_verified": False,
        "is_active": True,
        "has_voted_in": [],
        "registered_at": str(datetime.datetime.now()),
        "role": "voter",
    }

    ctx.voters.add(vid, voter)

    return True, voter_card


def get_all(ctx):
    return ctx.voters.get_all()


def get_by_id(ctx, vid: int):
    return ctx.voters.get_by_id(vid)


def verify(ctx, vid: int) -> bool:
    """Verify a voter account."""
    voter = ctx.voters.get_by_id(vid)

    if not voter:
        return False

    voter["is_verified"] = True
    return True


def verify_all(ctx, vid_list) -> int:
    """Verify multiple voters."""
    count = 0

    for vid in vid_list:
        voter = ctx.voters.get_by_id(vid)

        if voter and not voter.get("is_verified"):
            voter["is_verified"] = True
            count += 1

    return count


def deactivate(ctx, vid: int) -> bool:
    """Deactivate voter account."""
    voter = ctx.voters.get_by_id(vid)

    if not voter:
        return False

    voter["is_active"] = False
    return True


def search_by_name(ctx, term: str):
    term = term.lower()

    return [
        v for v in ctx.voters.get_all().values()
        if term in (v.get("full_name") or "").lower()
    ]


def search_by_card(ctx, card: str):
    return [
        v for v in ctx.voters.get_all().values()
        if v.get("voter_card_number") == card
    ]


def search_by_national_id(ctx, nid: str):
    return [
        v for v in ctx.voters.get_all().values()
        if v.get("national_id") == nid
    ]


def search_by_station(ctx, sid: int):
    return [
        v for v in ctx.voters.get_all().values()
        if v.get("station_id") == sid
    ]


def update_password(ctx, vid: int, new_hashed_password: str) -> bool:
    """Update voter password."""
    voter = ctx.voters.get_by_id(vid)

    if not voter:
        return False

    voter["password"] = new_hashed_password
    return True