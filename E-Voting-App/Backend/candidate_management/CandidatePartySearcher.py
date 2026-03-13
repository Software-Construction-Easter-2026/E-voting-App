from utils import prompt
import DataStore 

class CandidatePartySearcher:

    @staticmethod
    def search():

        term = prompt("Enter party name: ").lower()

        return [
            c for c in DataStore.candidates.values()
            if term in c["party"].lower()
        ]