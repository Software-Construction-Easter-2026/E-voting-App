from utils import prompt

class CandidateSearchChoiceInput:

    @staticmethod
    def get():

        return prompt("\nChoice: ")