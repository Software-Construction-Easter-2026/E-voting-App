import DataStore
from utils import log_action

class CandidateLogger:

    @staticmethod
    def log_creation(candidate):

        log_action(
            "CREATE_CANDIDATE",
            DataStore.current_user["username"],
            f"Created candidate: {candidate['full_name']} (ID: {candidate['id']})"
        )