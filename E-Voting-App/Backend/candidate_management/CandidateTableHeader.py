from utils import table_header, table_divider, THEME_ADMIN

class CandidateTableHeader:

    @staticmethod
    def CandidateTableHeader():

        table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}",
            THEME_ADMIN
        )

        table_divider(85, THEME_ADMIN)