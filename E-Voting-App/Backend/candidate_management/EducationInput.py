import datetime
import DataStore
from utils import prompt, error, pause, subheader, THEME_ADMIN_ACCENT, THEME_ADMIN, RESET

class EducationInput:

    @staticmethod
    def get_EducationInput():

        subheader("Education Levels", THEME_ADMIN_ACCENT)

        for i, level in enumerate(DataStore.REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")

        try:
            choice = int(prompt("Select education level: "))

            if choice < 1 or choice > len(DataStore.REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice.")
                pause()
                return None

            return DataStore.REQUIRED_EDUCATION_LEVELS[choice - 1]

        except ValueError:
            error("Invalid input.")
            pause()
            return None