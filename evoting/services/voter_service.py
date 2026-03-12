class VoterService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service

    def get_all(self):
        return dict(self._repo.voters)

    def get_by_id(self, vid):
        return self._repo.voters.get(vid)

    def verify(self, vid, verified_by_username):
        if vid not in self._repo.voters:
            return False
        if self._repo.voters[vid]["is_verified"]:
            return True, "already"
        self._repo.voters[vid]["is_verified"] = True
        name = self._repo.voters[vid]["full_name"]
        self._audit.log("VERIFY_VOTER", verified_by_username, f"Verified voter: {name}")
        return True, name

    def verify_all_pending(self, verified_by_username):
        unverified = [vid for vid, v in self._repo.voters.items() if not v["is_verified"]]
        for vid in unverified:
            self._repo.voters[vid]["is_verified"] = True
        self._audit.log("VERIFY_ALL_VOTERS", verified_by_username, f"Verified {len(unverified)} voters")
        return len(unverified)

    def get_unverified(self):
        return {vid: v for vid, v in self._repo.voters.items() if not v["is_verified"]}

    def deactivate(self, vid, deactivated_by_username):
        if vid not in self._repo.voters:
            return False
        if not self._repo.voters[vid]["is_active"]:
            return True, "already"
        self._repo.voters[vid]["is_active"] = False
        name = self._repo.voters[vid]["full_name"]
        self._audit.log("DEACTIVATE_VOTER", deactivated_by_username, f"Deactivated voter: {name}")
        return True, name

    def search_by_name(self, term):
        term = term.lower()
        return [v for v in self._repo.voters.values() if term in v["full_name"].lower()]

    def search_by_card(self, card_number):
        return [v for v in self._repo.voters.values() if v["voter_card_number"] == card_number]

    def search_by_national_id(self, national_id):
        return [v for v in self._repo.voters.values() if v["national_id"] == national_id]

    def search_by_station(self, station_id):
        return [v for v in self._repo.voters.values() if v["station_id"] == station_id]

    def update_password(self, voter_id, new_hashed_password):
        if voter_id in self._repo.voters:
            self._repo.voters[voter_id]["password"] = new_hashed_password
            return True
        return False

    def record_voted_in(self, voter_id, poll_id):
        for vid, v in self._repo.voters.items():
            if v["id"] == voter_id:
                if "has_voted_in" not in v:
                    v["has_voted_in"] = []
                if poll_id not in v["has_voted_in"]:
                    v["has_voted_in"].append(poll_id)
                return True
        return False
