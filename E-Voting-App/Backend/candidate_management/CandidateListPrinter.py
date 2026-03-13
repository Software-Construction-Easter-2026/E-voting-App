import DataStore
from utils import THEME_ADMIN, RESET, DIM

class CandidateListPrinter:

    @staticmethod
    def CandidateListPrinter():

        for cid, c in DataStore.candidates.items():

            print(
                f"  {THEME_ADMIN}{c['id']}.{RESET} "
                f"{c['full_name']} {DIM}({c['party']}){RESET}"
            )
