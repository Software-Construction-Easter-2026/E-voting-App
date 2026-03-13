import DataStore
from utils import log_action
from utils import AuditLogger

class CandidateUpdateLogger:

    @staticmethod
    def CandidateUpdateLogger(candidate, cid):

        log_action(
            "UPDATE_CANDIDATE",
            DataStore.current_user["username"],
            f"Updated candidate: {candidate['full_name']} (ID: {cid})"
        )