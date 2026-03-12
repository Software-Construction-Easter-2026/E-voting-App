import datetime

from evoting.core.constants import (
    MAX_CANDIDATE_AGE,
    MIN_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
)


class CandidateService:
    def __init__(self, repository, audit_service):
        self._repo = repository
        self._audit = audit_service

    def create(self, created_by_username, data):
        for c in self._repo.candidates.values():
            if c["national_id"] == data["national_id"]:
                return False, "duplicate_national_id"
        try:
            dob = datetime.datetime.strptime(data["dob_str"], "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return False, "invalid_date"
        if age < MIN_CANDIDATE_AGE:
            return False, ("underage", age)
        if age > MAX_CANDIDATE_AGE:
            return False, ("overage", age)
        if data["gender"].upper() not in ("M", "F", "OTHER"):
            return False, "invalid_gender"
        edu_choice = data.get("education_choice")
        if not (1 <= edu_choice <= len(REQUIRED_EDUCATION_LEVELS)):
            return False, "invalid_education"
        education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        if data.get("criminal_record", "").lower() == "yes":
            self._audit.log("CANDIDATE_REJECTED", created_by_username, f"Candidate {data['full_name']} rejected - criminal record")
            return False, "criminal_record"
        try:
            years_experience = int(data.get("years_experience", 0) or 0)
        except ValueError:
            years_experience = 0
        cid = self._repo.candidate_id_counter
        self._repo.candidates[cid] = {
            "id": cid,
            "full_name": data["full_name"],
            "national_id": data["national_id"],
            "date_of_birth": data["dob_str"],
            "age": age,
            "gender": data["gender"].upper(),
            "education": education,
            "party": data["party"],
            "manifesto": data.get("manifesto", ""),
            "address": data.get("address", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by_username,
        }
        self._repo.candidate_id_counter += 1
        self._audit.log("CREATE_CANDIDATE", created_by_username, f"Created candidate: {data['full_name']} (ID: {cid})")
        return True, cid

    def get_all(self):
        return dict(self._repo.candidates)

    def get_by_id(self, cid):
        return self._repo.candidates.get(cid)

    def update(self, cid, updated_by_username, updates):
        if cid not in self._repo.candidates:
            return False
        c = self._repo.candidates[cid]
        if updates.get("full_name"):
            c["full_name"] = updates["full_name"]
        if updates.get("party") is not None:
            c["party"] = updates["party"]
        if updates.get("manifesto") is not None:
            c["manifesto"] = updates["manifesto"]
        if updates.get("phone") is not None:
            c["phone"] = updates["phone"]
        if updates.get("email") is not None:
            c["email"] = updates["email"]
        if updates.get("address") is not None:
            c["address"] = updates["address"]
        if "years_experience" in updates and updates["years_experience"] is not None:
            try:
                c["years_experience"] = int(updates["years_experience"])
            except ValueError:
                pass
        self._audit.log("UPDATE_CANDIDATE", updated_by_username, f"Updated candidate: {c['full_name']} (ID: {cid})")
        return True

    def can_deactivate(self, cid):
        if cid not in self._repo.candidates:
            return False, "not_found"
        for poll in self._repo.polls.values():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        return False, "in_active_poll"
        return True, self._repo.candidates[cid]["full_name"]

    def deactivate(self, cid, deleted_by_username):
        ok, name = self.can_deactivate(cid)
        if not ok:
            return False, name
        self._repo.candidates[cid]["is_active"] = False
        self._audit.log("DELETE_CANDIDATE", deleted_by_username, f"Deactivated candidate: {name} (ID: {cid})")
        return True, name

    def search_by_name(self, term):
        term = term.lower()
        return [c for c in self._repo.candidates.values() if term in c["full_name"].lower()]

    def search_by_party(self, term):
        term = term.lower()
        return [c for c in self._repo.candidates.values() if term in c["party"].lower()]

    def search_by_education(self, education):
        return [c for c in self._repo.candidates.values() if c["education"] == education]

    def search_by_age_range(self, min_age, max_age):
        return [c for c in self._repo.candidates.values() if min_age <= c["age"] <= max_age]
