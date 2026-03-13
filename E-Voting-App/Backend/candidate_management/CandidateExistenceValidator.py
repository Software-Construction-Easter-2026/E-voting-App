import DataStore
from utils import error,pause

class CandidateExistenceValidator:

    @staticmethod
    def exists(cid):

        if cid not in DataStore.candidates:
            error("Candidate not found.")
            pause()
            return False

        return True