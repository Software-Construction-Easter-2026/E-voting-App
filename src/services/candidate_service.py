from datetime import datetime
from src.models.domain import Candidate

class CandidateService:
    MIN_CANDIDATE_AGE = 25
    MAX_CANDIDATE_AGE = 75
    REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]

    def __init__(self, data_store):
        self.ds = data_store
        
    def create_candidate(self, current_user, full_name, national_id, dob_str, gender, edu_choice, party, manifesto, address, phone, email, criminal_record, years_experience):
        if not full_name: return False, "Name cannot be empty."
        if not national_id: return False, "National ID cannot be empty."
        
        for c in self.ds.candidates.values():
            if c.national_id == national_id: return False, "A candidate with this National ID already exists."
            
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.now() - dob).days // 365
        except ValueError:
            return False, "Invalid date format."
            
        if age < self.MIN_CANDIDATE_AGE: return False, f"Candidate must be at least {self.MIN_CANDIDATE_AGE} years old. Current age: {age}"
        if age > self.MAX_CANDIDATE_AGE: return False, f"Candidate must not be older than {self.MAX_CANDIDATE_AGE}. Current age: {age}"
        
        if edu_choice < 1 or edu_choice > len(self.REQUIRED_EDUCATION_LEVELS): return False, "Invalid choice."
        education = self.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        
        if criminal_record.lower() == "yes":
            self.ds.log_action("CANDIDATE_REJECTED", current_user.username, f"Candidate {full_name} rejected - criminal record")
            return False, "Candidates with criminal records are not eligible."
            
        try: years_experience = int(years_experience)
        except ValueError: years_experience = 0
        
        cid = self.ds.candidate_id_counter
        candidate = Candidate(
            id=cid,
            full_name=full_name, national_id=national_id, date_of_birth=dob_str, age=age,
            gender=gender, education=education, party=party, manifesto=manifesto,
            address=address, phone=phone, email=email, has_criminal_record=False,
            years_experience=years_experience, is_active=True, is_approved=True,
            created_at=str(datetime.now()), created_by=current_user.username
        )
        self.ds.candidates[cid] = candidate
        self.ds.candidate_id_counter += 1
        
        self.ds.log_action("CREATE_CANDIDATE", current_user.username, f"Created candidate: {full_name} (ID: {cid})")
        self.ds.save_data()
        
        return True, f"Candidate '{full_name}' created successfully! ID: {cid}"

    def update_candidate(self, current_user, cid, new_name, new_party, new_manifesto, new_phone, new_email, new_address, new_exp):
        if cid not in self.ds.candidates: return False, "Candidate not found."
        c = self.ds.candidates[cid]
        
        if new_name: c.full_name = new_name
        if new_party: c.party = new_party
        if new_manifesto: c.manifesto = new_manifesto
        if new_phone: c.phone = new_phone
        if new_email: c.email = new_email
        if new_address: c.address = new_address
        if new_exp:
            try: c.years_experience = int(new_exp)
            except ValueError: pass
            
        self.ds.log_action("UPDATE_CANDIDATE", current_user.username, f"Updated candidate: {c.full_name} (ID: {cid})")
        self.ds.save_data()
        return True, f"Candidate '{c.full_name}' updated successfully!"

    def delete_candidate(self, current_user, cid):
        if cid not in self.ds.candidates: return False, "Candidate not found."
        
        # Check active polls
        for poll in self.ds.polls.values():
            if poll.status == "open":
                for pos in poll.positions:
                    if cid in pos.get("candidate_ids", []):
                        return False, f"Cannot delete - candidate is in active poll: {poll.title}"
                        
        deleted_name = self.ds.candidates[cid].full_name
        self.ds.candidates[cid].is_active = False
        
        self.ds.log_action("DELETE_CANDIDATE", current_user.username, f"Deactivated candidate: {deleted_name} (ID: {cid})")
        self.ds.save_data()
        return True, f"Candidate '{deleted_name}' has been deactivated."

    def search_candidates(self, choice, term=None, edu_choice=None, min_age=None, max_age=None):
        results = []
        if choice == "1" and term:
            results = [c for c in self.ds.candidates.values() if term.lower() in c.full_name.lower()]
        elif choice == "2" and term:
            results = [c for c in self.ds.candidates.values() if term.lower() in c.party.lower()]
        elif choice == "3" and edu_choice is not None:
             if 1 <= edu_choice <= len(self.REQUIRED_EDUCATION_LEVELS):
                edu = self.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = [c for c in self.ds.candidates.values() if c.education == edu]
        elif choice == "4" and min_age is not None and max_age is not None:
             results = [c for c in self.ds.candidates.values() if min_age <= c.age <= max_age]
        return results
