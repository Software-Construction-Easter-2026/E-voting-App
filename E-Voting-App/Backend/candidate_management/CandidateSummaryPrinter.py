import DataStore
from utils import DIM, RESET

class CandidateSummaryPrinter:

    @staticmethod
    def CandidateSummaryPrinter():

        print(f"\n  {DIM}Total Candidates: {len(DataStore.candidates)}{RESET}")