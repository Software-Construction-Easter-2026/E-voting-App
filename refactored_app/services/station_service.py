"""Voting station CRUD."""

import datetime
from services.auth_service import current_user
from services import validation


def create(ctx, data: dict) -> tuple[bool, str]:
    name = (data.get("name") or "").strip()
    if not name:
        return False, "Name cannot be empty."
    location = (data.get("location") or "").strip()
    if not location:
        return False, "Location cannot be empty."
    capacity = data.get("capacity")
    if not isinstance(capacity, int) or capacity <= 0:
        return False, "Capacity must be positive."
    contact = (data.get("contact") or "").strip()
    if contact and not validation.is_valid_phone(contact):
        return False, "Contact must start with 07 and have 10 digits (e.g. 0712345678)."
    contact = validation.normalize_phone(contact) if contact else ""
    sid = ctx.stations.next_id()
    station = {
        "id": sid,
        "name": name,
        "location": location,
        "region": data.get("region", ""),
        "capacity": capacity,
        "registered_voters": 0,
        "supervisor": data.get("supervisor", ""),
        "contact": contact,
        "opening_time": data.get("opening_time", ""),
        "closing_time": data.get("closing_time", ""),
        "is_active": True,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_user["username"] if current_user else "",
    }
    ctx.stations.add(sid, station)
    return True, str(sid)


def get_all(ctx):
    return ctx.stations.get_all()


def get_by_id(ctx, sid: int):
    return ctx.stations.get_by_id(sid)


def update(ctx, sid: int, updates: dict) -> tuple[bool, str]:
    s = ctx.stations.get_by_id(sid)
    if not s:
        return False, "Station not found."
    for key in ("name", "location", "region", "capacity", "supervisor", "contact"):
        if key in updates and updates[key] is not None:
            s[key] = updates[key]
    return True, ""


def count_voters_at_station(ctx, sid: int) -> int:
    return sum(1 for v in ctx.voters.get_all().values() if v.get("station_id") == sid)


def deactivate(ctx, sid: int) -> bool:
    s = ctx.stations.get_by_id(sid)
    if not s:
        return False
    s["is_active"] = False
    return True
