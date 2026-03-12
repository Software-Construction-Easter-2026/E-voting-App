"""Poll CRUD, open/close, assign candidates."""

import datetime
from services.auth_service import current_user
from services import validation


def create(ctx, data: dict) -> tuple[bool, str]:
    title = (data.get("title") or "").strip()
    if not title:
        return False, "Title cannot be empty."

    start_date = (data.get("start_date") or "").strip()
    end_date = (data.get("end_date") or "").strip()

    ok, err = validation.validate_date(start_date, allow_future=True)
    if not ok:
        return False, err or "Invalid start date format. Use YYYY-MM-DD."

    ok, err = validation.validate_date(end_date, allow_future=True)
    if not ok:
        return False, err or "Invalid end date format. Use YYYY-MM-DD."

    sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    if ed <= sd:
        return False, "End date must be after start date."

    position_ids = list(set(data.get("position_ids", [])))
    station_ids = list(set(data.get("station_ids", [])))

    if not position_ids:
        return False, "No valid positions selected."

    if not station_ids:
        return False, "No voting stations selected."

    positions_data = ctx.positions.get_all()
    poll_positions = []

    for pid in position_ids:
        pos = positions_data.get(pid)
        if pos and pos.get("is_active"):
            poll_positions.append({
                "position_id": pid,
                "position_title": pos["title"],
                "candidate_ids": [],
                "max_winners": pos["max_winners"],
            })

    if not poll_positions:
        return False, "No valid positions selected."

    poll_id = ctx.polls.next_id()

    poll = {
        "id": poll_id,
        "title": title,
        "description": data.get("description", ""),
        "election_type": data.get("election_type", ""),
        "start_date": start_date,
        "end_date": end_date,
        "positions": poll_positions,
        "station_ids": station_ids,
        "status": "draft",
        "total_votes_cast": 0,
        "created_at": str(datetime.datetime.now()),
        "created_by": current_user["username"] if current_user else "",
    }

    ctx.polls.add(poll_id, poll)

    return True, str(poll_id)


def get_all(ctx):
    return ctx.polls.get_all()


def get_by_id(ctx, pid: int):
    return ctx.polls.get_by_id(pid)


def update(ctx, pid: int, updates: dict) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") == "open":
        return False, "Cannot update an open poll. Close it first."

    if poll.get("status") == "closed" and (poll.get("total_votes_cast") or 0) > 0:
        return False, "Cannot update a poll with votes."

    if "start_date" in updates and updates["start_date"] is not None:
        ok, err = validation.validate_date(
            (updates["start_date"] or "").strip(),
            allow_future=True,
        )
        if not ok:
            return False, err or "Invalid start date format. Use YYYY-MM-DD."

    if "end_date" in updates and updates["end_date"] is not None:
        ok, err = validation.validate_date(
            (updates["end_date"] or "").strip(),
            allow_future=True,
        )
        if not ok:
            return False, err or "Invalid end date format. Use YYYY-MM-DD."

    for key in ("title", "description", "election_type", "start_date", "end_date"):
        if key in updates and updates[key] is not None:
            value = updates[key]

            if key in ("start_date", "end_date"):
                poll[key] = (value or "").strip()
            else:
                poll[key] = value

    return True, ""


def delete(ctx, pid: int) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") == "open":
        return False, "Cannot delete an open poll. Close it first."

    ctx.polls.remove(pid)
    ctx.votes.remove_by_poll_id(pid)

    return True, ""


def open_poll(ctx, pid: int) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") != "draft":
        return False, "Only draft polls can be opened."

    if not any(pos.get("candidate_ids") for pos in poll.get("positions", [])):
        return False, "Cannot open - no candidates assigned."

    poll["status"] = "open"

    return True, ""


def close_poll(ctx, pid: int) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") != "open":
        return False, "Poll is not open."

    poll["status"] = "closed"

    return True, ""


def reopen_poll(ctx, pid: int) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") != "closed":
        return False, "Only closed polls can be reopened."

    poll["status"] = "open"

    return True, ""


def assign_candidates_to_position(ctx, pid: int, position_index: int, candidate_ids: list) -> tuple[bool, str]:
    poll = ctx.polls.get_by_id(pid)

    if not poll:
        return False, "Poll not found."

    if poll.get("status") == "open":
        return False, "Cannot modify candidates of an open poll."

    positions = poll.get("positions", [])

    if position_index < 0 or position_index >= len(positions):
        return False, "Invalid position."

    positions[position_index]["candidate_ids"] = list(set(candidate_ids))

    return True, ""