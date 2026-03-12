"""Position CRUD."""

import datetime
from models.constants import MIN_CANDIDATE_AGE
from services.auth_service import current_user


def create(ctx, data: dict) -> tuple[bool, str]:
    title = (data.get("title") or "").strip()
    if not title:
        return False, "Title cannot be empty."
    level = (data.get("level") or "").lower()
    if level not in ("national", "regional", "local"):
        return False, "Invalid level."
    max_winners = data.get("max_winners")
    if not isinstance(max_winners, int) or max_winners <= 0:
        return False, "Must be at least 1."
    min_age = data.get("min_candidate_age")
    if min_age is None:
        min_age = MIN_CANDIDATE_AGE
    pid = ctx.positions.next_id()
    position = {
        "id": pid,
        "title": title,
        "description": data.get("description", ""),
        "level": level.capitalize(),
        "max_winners": max_winners,
        "min_candidate_age": min_age,
        "is_active": True,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_user["username"] if current_user else "",
    }
    ctx.positions.add(pid, position)
    return True, str(pid)


def get_all(ctx):
    return ctx.positions.get_all()


def get_by_id(ctx, pid: int):
    return ctx.positions.get_by_id(pid)


def update(ctx, pid: int, updates: dict) -> tuple[bool, str]:
    p = ctx.positions.get_by_id(pid)
    if not p:
        return False, "Position not found."
    for key in ("title", "description", "level", "max_winners"):
        if key in updates and updates[key] is not None:
            if key == "level" and updates[key].lower() in ("national", "regional", "local"):
                p[key] = updates[key].capitalize()
            else:
                p[key] = updates[key]
    return True, ""


def can_delete(ctx, pid: int) -> tuple[bool, str]:
    for poll in ctx.polls.get_all().values():
        for pos in poll.get("positions", []):
            if pos.get("position_id") == pid and poll.get("status") == "open":
                return False, f"Cannot delete - in active poll: {poll['title']}"
    return True, ""


def deactivate(ctx, pid: int) -> bool:
    p = ctx.positions.get_by_id(pid)
    if not p:
        return False
    p["is_active"] = False
    return True
