"""
Admin menu: Candidate Management (Create, View, Update, Delete, Search).
Single responsibility: only candidate-related admin screens.
"""
import datetime

from src.config.constants import (
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    DIM,
    BOLD,
    RESET,
    MIN_CANDIDATE_AGE,
    MAX_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
)
from src.services.candidate_service import CandidateService
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminCandidateHandlers(AdminHandlerBase):
    """Handles admin options 1–5: candidate CRUD and search. Uses CandidateService."""

    def __init__(self, repo, session: dict):
        super().__init__(repo, session)
        self.candidate_service = CandidateService(repo)

    def create_candidate(self) -> None:
        self.clear_screen()
        self.ui.header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name = self.prompt("Full Name: ")
        if not full_name:
            self.error("Name cannot be empty.")
            self.pause()
            return
        national_id = self.prompt("National ID: ")
        if not national_id:
            self.error("National ID cannot be empty.")
            self.pause()
            return
        # Duplicate check (same order as original): before DOB
        for c in self.repo.candidates.values():
            if c["national_id"] == national_id:
                self.error("A candidate with this National ID already exists.")
                self.pause()
                return
        dob_str = self.prompt("Date of Birth (YYYY-MM-DD): ")
        # Validate DOB and age immediately after input (same flow as original: error in red, then pause/return)
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            self.error("Invalid date format.")
            self.pause()
            return
        if age < MIN_CANDIDATE_AGE:
            self.error(f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}")
            self.pause()
            return
        if age > MAX_CANDIDATE_AGE:
            self.error(f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}")
            self.pause()
            return
        gender = self.prompt("Gender (M/F/Other): ").upper()
        self.ui.subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(self.prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                self.error("Invalid choice.")
                self.pause()
                return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        party = self.prompt("Political Party/Affiliation: ")
        manifesto = self.prompt("Brief Manifesto/Bio: ")
        address = self.prompt("Address: ")
        phone = self.prompt("Phone: ")
        email = self.prompt("Email: ")
        criminal_record = self.prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            self.error("Candidates with criminal records are not eligible.")
            self.audit.log_action("CANDIDATE_REJECTED", self.user["username"], f"Candidate {full_name} rejected - criminal record")
            self.pause()
            return
        years_experience = self.prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_experience)
        except ValueError:
            years_experience = 0
        ok, msg = self.candidate_service.create_candidate(
            self.user["username"], full_name, national_id, dob_str, gender, education,
            party, manifesto, address, phone, email, False, years_experience
        )
        if ok:
            self.audit.log_action("CREATE_CANDIDATE", self.user["username"], msg)
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def view_all_candidates(self) -> None:
        self.clear_screen()
        self.ui.header("ALL CANDIDATES", THEME_ADMIN)
        if not self.repo.candidates:
            print()
            self.info("No candidates found.")
            self.pause()
            return
        print()
        self.ui.table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        self.ui.table_divider(85, THEME_ADMIN)
        for cid, c in self.repo.candidates.items():
            status = self.ui.status_badge("Active", True) if c["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
        print(f"\n  {DIM}Total Candidates: {len(self.repo.candidates)}{RESET}")
        self.pause()

    def update_candidate(self) -> None:
        self.clear_screen()
        self.ui.header("UPDATE CANDIDATE", THEME_ADMIN)
        if not self.repo.candidates:
            print()
            self.info("No candidates found.")
            self.pause()
            return
        print()
        for cid, c in self.repo.candidates.items():
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
        try:
            cid = int(self.prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if cid not in self.repo.candidates:
            self.error("Candidate not found.")
            self.pause()
            return
        c = self.repo.candidates[cid]
        print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
        self.info("Press Enter to keep current value\n")
        new_name = self.prompt(f"Full Name [{c['full_name']}]: ")
        new_party = self.prompt(f"Party [{c['party']}]: ")
        new_manifesto = self.prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
        new_phone = self.prompt(f"Phone [{c['phone']}]: ")
        new_email = self.prompt(f"Email [{c['email']}]: ")
        new_address = self.prompt(f"Address [{c['address']}]: ")
        new_exp = self.prompt(f"Years Experience [{c['years_experience']}]: ")
        years_experience = None
        if new_exp:
            try:
                years_experience = int(new_exp)
            except ValueError:
                self.warning("Invalid number, keeping old value.")
        ok, msg = self.candidate_service.update_candidate(
            cid, self.user["username"],
            full_name=new_name or None, party=new_party or None, manifesto=new_manifesto or None,
            phone=new_phone or None, email=new_email or None, address=new_address or None,
            years_experience=years_experience
        )
        if ok:
            self.audit.log_action("UPDATE_CANDIDATE", self.user["username"], f"Updated candidate: {c['full_name']} (ID: {cid})")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def delete_candidate(self) -> None:
        self.clear_screen()
        self.ui.header("DELETE CANDIDATE", THEME_ADMIN)
        if not self.repo.candidates:
            print()
            self.info("No candidates found.")
            self.pause()
            return
        print()
        for cid, c in self.repo.candidates.items():
            status = self.ui.status_badge("Active", True) if c["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
        try:
            cid = int(self.prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if cid not in self.repo.candidates:
            self.error("Candidate not found.")
            self.pause()
            return
        confirm = self.prompt(f"Are you sure you want to delete '{self.repo.candidates[cid]['full_name']}'? (yes/no): ").lower()
        if confirm != "yes":
            self.info("Deletion cancelled.")
            self.pause()
            return
        ok, msg = self.candidate_service.delete_candidate(cid, self.user["username"])
        if ok:
            self.audit.log_action("DELETE_CANDIDATE", self.user["username"], f"Deactivated candidate: {self.repo.candidates[cid]['full_name']} (ID: {cid})")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def search_candidates(self) -> None:
        self.clear_screen()
        self.ui.header("SEARCH CANDIDATES", THEME_ADMIN)
        self.ui.subheader("Search by", THEME_ADMIN_ACCENT)
        self.ui.menu_item(1, "Name", THEME_ADMIN)
        self.ui.menu_item(2, "Party", THEME_ADMIN)
        self.ui.menu_item(3, "Education Level", THEME_ADMIN)
        self.ui.menu_item(4, "Age Range", THEME_ADMIN)
        choice = self.prompt("\nChoice: ")
        results = []
        if choice == "1":
            term = self.prompt("Enter name to search: ").lower()
            results = self.candidate_service.search_by_name(term)
        elif choice == "2":
            term = self.prompt("Enter party name: ").lower()
            results = self.candidate_service.search_by_party(term)
        elif choice == "3":
            self.ui.subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(self.prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self.candidate_service.search_by_education(edu)
            except (ValueError, IndexError):
                self.error("Invalid choice.")
                self.pause()
                return
        elif choice == "4":
            try:
                min_age = int(self.prompt("Min age: "))
                max_age = int(self.prompt("Max age: "))
                results = self.candidate_service.search_by_age_range(min_age, max_age)
            except ValueError:
                self.error("Invalid input.")
                self.pause()
                return
        else:
            self.error("Invalid choice.")
            self.pause()
            return
        if not results:
            print()
            self.info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            self.ui.table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            self.ui.table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
        self.pause()
