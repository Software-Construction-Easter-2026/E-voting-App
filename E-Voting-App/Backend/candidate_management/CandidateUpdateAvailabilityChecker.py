import DataStore
from utils import info, pause

class CandidateUpdateAvailabilityChecker:

    @staticmethod
    def has_candidates():

        if not DataStore.candidates:
            print()
            info("No candidates found.")
            pause()
            return False

        return True