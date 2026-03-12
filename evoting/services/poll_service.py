import datetime


class PollService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service

    def create(self, created_by_username, data):
        try:
            sd = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
            ed = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
            if ed <= sd:
                return False, "end_before_start"
        except ValueError:
            return False, "invalid_date"
        active_positions = {pid: p for pid, p in self._repo.positions.items() if p.get("is_active", True)}
        poll_positions = []
        for spid in data.get("position_ids", []):
            if spid not in active_positions:
                continue
            p = self._repo.positions[spid]
            poll_positions.append({
                "position_id": spid,
                "position_title": p["title"],
                "candidate_ids": [],
                "max_winners": p["max_winners"],
            })
        if not poll_positions:
            return False, "no_valid_positions"
        station_ids = data.get("station_ids", [])
        if not station_ids:
            return False, "no_stations"
        pid = self._repo.poll_id_counter
        self._repo.polls[pid] = {
            "id": pid,
            "title": data["title"],
            "description": data.get("description", ""),
            "election_type": data.get("election_type", ""),
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "positions": poll_positions,
            "station_ids": station_ids,
            "status": "draft",
            "total_votes_cast": 0,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by_username,
        }
        self._repo.poll_id_counter += 1
        self._audit.log("CREATE_POLL", created_by_username, f"Created poll: {data['title']} (ID: {pid})")
        return True, pid

    def get_all(self):
        return dict(self._repo.polls)

    def get_by_id(self, pid):
        return self._repo.polls.get(pid)

    def update(self, pid, updated_by_username, updates):
        if pid not in self._repo.polls:
            return False
        poll = self._repo.polls[pid]
        if poll["status"] == "open":
            return False, "poll_open"
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            return False, "poll_has_votes"
        if updates.get("title"):
            poll["title"] = updates["title"]
        if updates.get("description") is not None:
            poll["description"] = updates["description"]
        if updates.get("election_type"):
            poll["election_type"] = updates["election_type"]
        if updates.get("start_date"):
            try:
                datetime.datetime.strptime(updates["start_date"], "%Y-%m-%d")
                poll["start_date"] = updates["start_date"]
            except ValueError:
                pass
        if updates.get("end_date"):
            try:
                datetime.datetime.strptime(updates["end_date"], "%Y-%m-%d")
                poll["end_date"] = updates["end_date"]
            except ValueError:
                pass
        self._audit.log("UPDATE_POLL", updated_by_username, f"Updated poll: {poll['title']}")
        return True

    def delete(self, pid, deleted_by_username):
        if pid not in self._repo.polls:
            return False
        poll = self._repo.polls[pid]
        if poll["status"] == "open":
            return False, "poll_open"
        title = poll["title"]
        del self._repo.polls[pid]
        self._repo.votes[:] = [v for v in self._repo.votes if v["poll_id"] != pid]
        self._audit.log("DELETE_POLL", deleted_by_username, f"Deleted poll: {title}")
        return True, title

    def open_poll(self, pid, username):
        if pid not in self._repo.polls:
            return False, "not_found"
        poll = self._repo.polls[pid]
        if poll["status"] != "draft":
            return False, "not_draft"
        if not any(pos.get("candidate_ids") for pos in poll["positions"]):
            return False, "no_candidates"
        poll["status"] = "open"
        self._audit.log("OPEN_POLL", username, f"Opened poll: {poll['title']}")
        return True

    def close_poll(self, pid, username):
        if pid not in self._repo.polls:
            return False
        poll = self._repo.polls[pid]
        if poll["status"] != "open":
            return False
        poll["status"] = "closed"
        self._audit.log("CLOSE_POLL", username, f"Closed poll: {poll['title']}")
        return True

    def reopen_poll(self, pid, username):
        if pid not in self._repo.polls:
            return False
        poll = self._repo.polls[pid]
        if poll["status"] != "closed":
            return False
        poll["status"] = "open"
        self._audit.log("REOPEN_POLL", username, f"Reopened poll: {poll['title']}")
        return True

    def assign_candidates(self, pid, username, position_candidate_ids):
        if pid not in self._repo.polls:
            return False
        poll = self._repo.polls[pid]
        if poll["status"] == "open":
            return False, "poll_open"
        for pos in poll["positions"]:
            pos_id = pos["position_id"]
            if pos_id in position_candidate_ids:
                pos["candidate_ids"] = position_candidate_ids[pos_id]
        self._audit.log("ASSIGN_CANDIDATES", username, f"Updated candidates for poll: {poll['title']}")
        return True
