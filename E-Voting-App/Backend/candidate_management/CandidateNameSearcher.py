from utils import prompt
import DataStore

class CandidateNameSearcher:

    @staticmethod
    def search():

        term = prompt("Enter name to search: ").lower()

        return [
            c for c in DataStore.candidates.values()
            if term in c["full_name"].lower()
        ]