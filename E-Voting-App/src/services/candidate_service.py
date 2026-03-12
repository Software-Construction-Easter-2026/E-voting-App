"""
Candidate CRUD and search. Handles eligibility (age, education, criminal record).
Implemented as CandidateService(BaseService) for encapsulation and OOP.
"""
import datetime

from src.config.constants import (
    MIN_CANDIDATE_AGE,
    MAX_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
)
from src.services.base_service import BaseService


class CandidateService(BaseService):
    """
    Encapsulates candidate business rules: create, update, delete, search.
    All methods take current_username for audit; no UI.
    """

    def create_candidate(
        self,
        current_username: str,
        full_name: str,
        national_id: str,
        dob_str: str,
        gender: str,
        education: str,
        party: str,
        manifesto: str,
        address: str,
        phone: str,
        email: str,
        has_criminal_record: bool,
        years_experience: int,
    ) -> tuple[bool, str]:
        """Create candidate if eligible. Returns (success, message)."""
        if not full_name:
            return False, "Name cannot be empty."
        if not national_id:
            return False, "National ID cannot be empty."
        for c in self.repo.candidates.values():
            if c["national_id"] == national_id:
                return False, "A candidate with this National ID already exists."
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return False, "Invalid date format."
        if age < MIN_CANDIDATE_AGE:
            return False, f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"
        if age > MAX_CANDIDATE_AGE:
            return False, f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"
        if education not in REQUIRED_EDUCATION_LEVELS:
            return False, "Invalid education level."
        if has_criminal_record:
            return False, "criminal_record"

        cid = self.repo.candidate_id_counter
        self.repo.candidates[cid] = {
            "id": cid,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "education": education,
            "party": party,
            "manifesto": manifesto,
            "address": address,
            "phone": phone,
            "email": email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": current_username,
        }
        self.repo.candidate_id_counter += 1
        return True, f"Candidate '{full_name}' created successfully! ID: {cid}"

    def update_candidate(
        self,
        cid: int,
        current_username: str,
        full_name: str = None,
        party: str = None,
        manifesto: str = None,
        phone: str = None,
        email: str = None,
        address: str = None,
        years_experience: int = None,
    ) -> tuple[bool, str]:
        """Update candidate by ID. None means keep current."""
        if cid not in self.repo.candidates:
            return False, "Candidate not found."
        c = self.repo.candidates[cid]
        if full_name:
            c["full_name"] = full_name
        if party is not None:
            c["party"] = party
        if manifesto is not None:
            c["manifesto"] = manifesto
        if phone is not None:
            c["phone"] = phone
        if email is not None:
            c["email"] = email
        if address is not None:
            c["address"] = address
        if years_experience is not None:
            c["years_experience"] = years_experience
        return True, f"Candidate '{c['full_name']}' updated successfully!"

    def delete_candidate(self, cid: int, current_username: str) -> tuple[bool, str]:
        """Soft-delete (deactivate) candidate if not in active poll."""
        if cid not in self.repo.candidates:
            return False, "Candidate not found."
        for pid, poll in self.repo.polls.items():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        return False, f"Cannot delete - candidate is in active poll: {poll['title']}"
        name = self.repo.candidates[cid]["full_name"]
        self.repo.candidates[cid]["is_active"] = False
        return True, f"Candidate '{name}' has been deactivated."

    def search_by_name(self, term: str) -> list:
        return [c for c in self.repo.candidates.values() if term in c["full_name"].lower()]

    def search_by_party(self, term: str) -> list:
        return [c for c in self.repo.candidates.values() if term in c["party"].lower()]

    def search_by_education(self, education: str) -> list:
        return [c for c in self.repo.candidates.values() if c["education"] == education]

    def search_by_age_range(self, min_age: int, max_age: int) -> list:
        return [c for c in self.repo.candidates.values() if min_age <= c["age"] <= max_age]
