import DataStore

class CandidateDeactivator:

    @staticmethod
    def deactivate(cid):

        deleted_name = DataStore.candidates[cid]["full_name"]

        DataStore.candidates[cid]["is_active"] = False

        return deleted_name