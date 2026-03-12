import datetime


class StationService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service

    def create(self, created_by_username, data):
        sid = self._repo.station_id_counter
        self._repo.voting_stations[sid] = {
            "id": sid,
            "name": data["name"],
            "location": data["location"],
            "region": data.get("region", ""),
            "capacity": data["capacity"],
            "registered_voters": 0,
            "supervisor": data.get("supervisor", ""),
            "contact": data.get("contact", ""),
            "opening_time": data.get("opening_time", ""),
            "closing_time": data.get("closing_time", ""),
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by_username,
        }
        self._repo.station_id_counter += 1
        self._audit.log("CREATE_STATION", created_by_username, f"Created station: {data['name']} (ID: {sid})")
        return sid

    def get_all(self):
        return dict(self._repo.voting_stations)

    def get_by_id(self, sid):
        return self._repo.voting_stations.get(sid)

    def count_voters_at_station(self, sid):
        return sum(1 for v in self._repo.voters.values() if v["station_id"] == sid)

    def update(self, sid, updated_by_username, updates):
        if sid not in self._repo.voting_stations:
            return False
        s = self._repo.voting_stations[sid]
        if updates.get("name"):
            s["name"] = updates["name"]
        if updates.get("location") is not None:
            s["location"] = updates["location"]
        if updates.get("region") is not None:
            s["region"] = updates["region"]
        if updates.get("capacity") is not None:
            try:
                s["capacity"] = int(updates["capacity"])
            except ValueError:
                pass
        if updates.get("supervisor") is not None:
            s["supervisor"] = updates["supervisor"]
        if updates.get("contact") is not None:
            s["contact"] = updates["contact"]
        self._audit.log("UPDATE_STATION", updated_by_username, f"Updated station: {s['name']} (ID: {sid})")
        return True

    def deactivate(self, sid, deleted_by_username):
        if sid not in self._repo.voting_stations:
            return False
        name = self._repo.voting_stations[sid]["name"]
        self._repo.voting_stations[sid]["is_active"] = False
        self._audit.log("DELETE_STATION", deleted_by_username, f"Deactivated station: {name}")
        return True, name
