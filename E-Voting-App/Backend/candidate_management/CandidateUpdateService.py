import DataStore
from utils import clear_screen, header, THEME_ADMIN

from CandidateUpdateAvailabilityChecker import has_candidates
from CandidateListPrinter import CandidateListPrinter
from CandidateIdInput import CandidateIdInput
from CandidateFinder import CandidateFinder
from CandidateFieldUpdater import CandidateFieldUpdater
from CandidateUpdateLogger import CandidateUpdateLogger
from  CandidateUpdateSaver import CandidateUpdateSaver
from CandidateUpdateSuccess import CandidateUpdateSuccess


class CandidateUpdateService:

    @staticmethod
    def update_candidate():

        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)

        if not has_candidates():
            return

        print()

        CandidateListPrinter()

        cid = CandidateIdInput()
        if cid is None:
            return

        candidate = CandidateFinder(cid)
        if not candidate:
            return

        CandidateFieldUpdater(candidate)

        CandidateUpdateLogger(candidate, cid)

        CandidateUpdateSaver()

        CandidateUpdateSuccess(candidate)