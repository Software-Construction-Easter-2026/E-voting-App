import DataStore
from utils import clear_screen, header, success, pause, prompt
from utils import THEME_ADMIN

from get_full_name import get_full_name
from NationalIdInput import get_NationalIdInput
from AgeValidator import validate
from EducationInput import get_EducationInput
from CriminalRecordValidator import check_CriminalRecordValidator
from CandidateFactory import create_CandidateFactory
from CandidateRepository import save
from CandidateLogger import log_creation


class CandidateService:

    @staticmethod
    def create_candidate():

        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()

        # name
        full_name = get_full_name()
        if not full_name:
            return

        # national id
        national_id = get_NationalIdInput()
        if not national_id:
            return

        # check duplicate national ID
        for cid, c in DataStore.candidates.items():
            if c["national_id"] == national_id:
                print("A candidate with this National ID already exists.")
                pause()
                return

        # age validation
        dob_str, age = validate()
        if not dob_str:
            return

        # gender
        gender = prompt("Gender (M/F/Other): ").upper()

        # education
        education = get_EducationInput()
        if not education:
            return

        # other fields
        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")

        # criminal record check
        if not check_CriminalRecordValidator(full_name):
            return

        # experience
        years_experience = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_experience)
        except ValueError:
            years_experience = 0

        # create candidate
        candidate = create_CandidateFactory(
            DataStore.candidate_id_counter,
            full_name,
            national_id,
            dob_str,
            age,
            gender,
            education,
            party,
            manifesto,
            address,
            phone,
            email,
            years_experience
        )

        # save candidate
        save(candidate)

        # log action
        log_creation(candidate)

        print()
        success(f"Candidate '{full_name}' created successfully! ID: {candidate['id']}")

        pause()