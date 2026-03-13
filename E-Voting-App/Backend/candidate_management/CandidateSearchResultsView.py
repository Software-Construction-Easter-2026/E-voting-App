from utils import info, BOLD, RESET, THEME_ADMIN, table_header, table_divider

class CandidateSearchResultsView:

    @staticmethod
    def display(results):

        if not results:

            print()
            info("No candidates found matching your criteria.")
            return

        print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")

        table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}",
            THEME_ADMIN
        )

        table_divider(75, THEME_ADMIN)

        for c in results:

            print(
                f"  {c['id']:<5} "
                f"{c['full_name']:<25} "
                f"{c['party']:<20} "
                f"{c['age']:<5} "
                f"{c['education']:<20}"
            )