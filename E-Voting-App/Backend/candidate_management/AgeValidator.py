import datetime

import DataStore
from utils import prompt, error, pause

class AgeValidator:

    @staticmethod
    def validate():
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")

        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            error("Invalid date format.")
            pause()
            return None, None

        if age < DataStore.MIN_CANDIDATE_AGE:
            error(f"Candidate must be at least {DataStore.MIN_CANDIDATE_AGE} years old. Current age: {age}")
            pause()
            return None, None

        if age > DataStore.MAX_CANDIDATE_AGE:
            error(f"Candidate must not be older than {DataStore.MAX_CANDIDATE_AGE}. Current age: {age}")
            pause()
            return None, None

        return dob_str, age