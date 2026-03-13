import datetime


class AdminService:
    def __init__(self, repository, audit_service, auth_service):
        self._repo = repository
        self._audit = audit_service
        self._auth = auth_service

    def create(self, created_by_username, data):
        if self._auth.current_user and self._auth.current_user.get("role") != "super_admin":
            return False, "forbidden"
        for a in self._repo.admins.values():
            if a["username"] == data["username"]:
                return False, "duplicate_username"
        if len(data["password"]) < 6:
            return False, "short_password"
        role_map = {"1": "super_admin", "2": "election_officer", "3": "station_manager", "4": "auditor"}
        role = role_map.get(data.get("role_choice", ""))
        if not role:
            return False, "invalid_role"
        aid = self._repo.admin_id_counter
        self._repo.admins[aid] = {
            "id": aid,
            "username": data["username"],
            "password": self._auth.hash_password(data["password"]),
            "full_name": data["full_name"],
            "email": data.get("email", ""),
            "role": role,
            "created_at": str(datetime.datetime.now()),
            "is_active": True,
        }
        self._repo.admin_id_counter += 1
        self._audit.log("CREATE_ADMIN", created_by_username, f"Created admin: {data['username']} (Role: {role})")
        return True, (data["username"], role)

    def get_all(self):
        return dict(self._repo.admins)

    def deactivate(self, aid, deactivated_by_username, current_user_id):
        if self._auth.current_user and self._auth.current_user.get("role") != "super_admin":
            return False, "forbidden"
        if aid not in self._repo.admins:
            return False, "not_found"
        if aid == current_user_id:
            return False, "self"
        self._repo.admins[aid]["is_active"] = False
        name = self._repo.admins[aid]["username"]
        self._audit.log("DEACTIVATE_ADMIN", deactivated_by_username, f"Deactivated admin: {name}")
        return True, name
