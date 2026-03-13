class CandidateRowPrinter:

    @staticmethod
    def CandidateRowPrinter(candidate, status):

        print(
            f"  {candidate['id']:<5} "
            f"{candidate['full_name']:<25} "
            f"{candidate['party']:<20} "
            f"{candidate['age']:<5} "
            f"{candidate['education']:<20} "
            f"{status}"
        )