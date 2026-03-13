from utils import prompt, error, pause 

class CandidateAgeRangeInput:

    @staticmethod
    def get():

        try:

            min_age = int(prompt("Min age: "))
            max_age = int(prompt("Max age: "))

            return min_age, max_age

        except ValueError:

            error("Invalid input.")
            pause()
            return None