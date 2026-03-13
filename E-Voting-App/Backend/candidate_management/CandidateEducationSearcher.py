import DataStore

class CandidateEducationSearcher:

    @staticmethod
    def search(education):

        return [
            c for c in DataStore.candidates.values()
            if c["education"] == education
        ]