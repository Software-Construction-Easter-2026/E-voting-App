import DataStore
from utils import prompt

class CandidateDeleteConfirmation:

    @staticmethod
    def confirm(cid):

        confirm = prompt(
            f"Are you sure you want to delete '{DataStore.candidates[cid]['full_name']}'? (yes/no): "
        ).lower()

        return confirm == "yes"