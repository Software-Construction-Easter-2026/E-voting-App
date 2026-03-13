import DataStore
from utils import info,pause, status_badge, THEME_ADMIN, RESET, DIM

class CandidateListView:

    @staticmethod
    def display_CandidateListView():

        if not DataStore.candidates:
            print()
            info("No candidates found.")
            pause()
            return False

        print()

        for cid, c in DataStore.candidates.items():

            status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)

            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")

        return True