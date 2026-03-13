
from utils import prompt, error, pause, log_action
import DataStore


class CriminalRecordValidator:

    @staticmethod
    def check_CriminalRecordValidator(full_name):

        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()

        if criminal_record == "yes":

            error("Candidates with criminal records are not eligible.")

            log_action(
                "CANDIDATE_REJECTED",
                DataStore.current_user["username"],
                f"Candidate {full_name} rejected - criminal record"
            )

            pause()
            return False

        return True