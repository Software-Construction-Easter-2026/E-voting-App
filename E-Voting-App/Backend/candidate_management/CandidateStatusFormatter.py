from utils import status_badge

class CandidateStatusFormatter:

    @staticmethod
    def CandidateStatusFormatter(is_active):

        if is_active:
            return status_badge("Active", True)

        return status_badge("Inactive", False)
    