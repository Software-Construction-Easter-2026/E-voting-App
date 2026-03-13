import DataStore
from utils import clear_screen, header, pause, THEME_ADMIN

from CandidateExistenceChecker import has_candidates
from CandidateTableHeader import CandidateTableHeader
from CandidateListRenderer import CandidateListRenderer
from CandidateSummaryPrinter import CandidateSummaryPrinter


class CandidateViewService:

    @staticmethod
    def view_all():

        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)

        if not has_candidates():
            return

        print()

        CandidateTableHeader()

        CandidateListRenderer()

        CandidateSummaryPrinter()

        pause()