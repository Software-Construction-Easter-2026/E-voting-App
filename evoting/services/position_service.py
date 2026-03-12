import datetime

from evoting.core.constants import MIN_CANDIDATE_AGE


class PositionService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service

    def create(self, created_by_username, data):
        level = data["level"].lower()
        if level not in ("national", "regional", "local"):
            return False, "invalid_level"
        max_winners = data.get("max_winners", 1)
        if max_winners <= 0:
            return False, "invalid_seats"
        min_age = data.get("min_candidate_age") or MIN_CANDIDATE_AGE
        pid = self._repo.position_id_counter
        self._repo.positions[pid] = {
            "id": pid,
            "title": data["title"],
            "description": data.get("description", ""),
            "level": level.capitalize(),
            "max_winners": max_winners,
            "min_candidate_age": min_age,
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by_username,
        }
        self._repo.position_id_counter += 1
        self._audit.log("CREATE_POSITION", created_by_username, f"Created position: {data['title']} (ID: {pid})")
        return True, pid

    def get_all(self):
        return dict(self._repo.positions)

    def get_by_id(self, pid):
        return self._repo.positions.get(pid)

    def update(self, pid, updated_by_username, updates):
        if pid not in self._repo.positions:
            return False
        p = self._repo.positions[pid]
        if updates.get("title"):
            p["title"] = updates["title"]
        if updates.get("description") is not None:
            p["description"] = updates["description"]
        if updates.get("level"):
            low = updates["level"].lower()
            if low in ("national", "regional", "local"):
                p["level"] = low.capitalize()
        if updates.get("max_winners") is not None:
            try:
                p["max_winners"] = int(updates["max_winners"])
            except ValueError:
                pass
        self._audit.log("UPDATE_POSITION", updated_by_username, f"Updated position: {p['title']}")
        return True

    def deactivate(self, pid, deleted_by_username):
        if pid not in self._repo.positions:
            return False
        for poll in self._repo.polls.values():
            for pp in poll.get("positions", []):
                if pp["position_id"] == pid and poll["status"] == "open":
                    return False, "in_active_poll"
        self._repo.positions[pid]["is_active"] = False
        title = self._repo.positions[pid]["title"]
        self._audit.log("DELETE_POSITION", deleted_by_username, f"Deactivated position: {title}")
        return True, title
