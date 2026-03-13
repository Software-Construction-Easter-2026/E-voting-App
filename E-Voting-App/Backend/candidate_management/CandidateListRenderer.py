import DataStore
from CandidateStatusFormatter import CandidateStatusFormatter
from CandidateRowPrinter import CandidateRowPrinter

class CandidateListRenderer:

    @staticmethod
    def CandidateListRenderer():

        for cid, candidate in DataStore.candidates.items():

            status = CandidateStatusFormatter.format(candidate["is_active"])

            CandidateRowPrinter.print(candidate, status)