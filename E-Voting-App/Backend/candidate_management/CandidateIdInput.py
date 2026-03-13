from utils import prompt, error, pause

class CandidateIdInput:

    @staticmethod
    def CandidateIdInput():

        try:
            return int(prompt("\nEnter Candidate ID to update: "))

        except ValueError:
            error("Invalid input.")
            pause()
            return None