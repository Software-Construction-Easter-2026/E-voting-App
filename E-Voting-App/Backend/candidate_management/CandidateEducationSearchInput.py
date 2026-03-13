from utils import subheader, THEME_ADMIN, error, pause, prompt, THEME_ADMIN_ACCENT, RESET
import DataStore


class CandidateEducationSearchInput:

    @staticmethod
    def get():

        subheader("Education Levels", THEME_ADMIN_ACCENT)

        for i, level in enumerate(DataStore.REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")

        try:
            edu_choice = int(prompt("Select: "))

            return DataStore.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]

        except (ValueError, IndexError):

            error("Invalid choice.")
            pause()
            return None