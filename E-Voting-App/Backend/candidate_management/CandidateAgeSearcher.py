import DataStore 

class CandidateAgeSearcher:

    @staticmethod
    def search(min_age, max_age):

        return [
            c for c in DataStore.candidates.values()
            if min_age <= c["age"] <= max_age
        ]