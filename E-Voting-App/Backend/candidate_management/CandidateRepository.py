import DataStore
from utils import pause

class CandidateRepository:

    @staticmethod
    def save(candidate):

        global candidate_id_counter

        DataStore.candidates[candidate_id_counter] = candidate
        candidate_id_counter += 1
        pause()