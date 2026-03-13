import DataStore
from utils import error, pause

class CandidateFinder:

    @staticmethod
    def CandidateFinder(cid):

        if cid not in DataStore.candidates:
            error("Candidate not found.")
            pause()
            return None

        return DataStore.candidates[cid]