from utils import AuditLogger
import DataStore

class CandidateDeleteLogger:

    @staticmethod
    def log(cid, deleted_name):

        AuditLogger.log_action(
            "DELETE_CANDIDATE",
            DataStore.current_user["username"],
            f"Deactivated candidate: {deleted_name} (ID: {cid})"
        )