from utils import ScreenHelper, header, THEME_ADMIN, error, pause
from CandidateSearchChoiceInput import CandidateSearchChoiceInput
from CandidateSearchMenu import CandidateSearchMenu
from CandidateNameSearcher import search
from CandidatePartySearcher import CandidatePartySearcher
from CandidateEducationSearchInput import CandidateEducationSearchInput
from  CandidateEducationSearcher import  CandidateEducationSearcher
from CandidateAgeRangeInput import CandidateAgeRangeInput
from CandidateAgeSearcher import CandidateAgeSearcher
from CandidateSearchResultsView import CandidateSearchResultsView



class SearchCandidates:

    def execute(self):

        ScreenHelper.clear_screen()

        header("SEARCH CANDIDATES", THEME_ADMIN)

        CandidateSearchMenu()

        choice = CandidateSearchChoiceInput()

        results = []

        if choice == "1":

            results = search()

        elif choice == "2":

            results = CandidatePartySearcher()

        elif choice == "3":

            education = CandidateEducationSearchInput.get()

            if education is None:
                return

            results = CandidateEducationSearcher(education)

        elif choice == "4":

            age_range = CandidateAgeRangeInput()

            if age_range is None:
                return

            min_age, max_age = age_range

            results = CandidateAgeSearcher(min_age, max_age)

        else:

            error("Invalid choice.")
            pause()
            return

        CandidateSearchResultsView(results)

        pause()