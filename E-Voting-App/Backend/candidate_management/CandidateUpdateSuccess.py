from utils import success, pause

class CandidateUpdateSuccess:

    @staticmethod
    def CandidateUpdateSuccess(candidate):

        print()
        success(f"Candidate '{candidate['full_name']}' updated successfully!")
        pause()

