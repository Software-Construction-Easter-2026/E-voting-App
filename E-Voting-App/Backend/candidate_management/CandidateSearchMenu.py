from utils import menu_item, subheader, THEME_ADMIN, THEME_ADMIN_ACCENT

class CandidateSearchMenu:

    @staticmethod
    def display():

        subheader("Search by", THEME_ADMIN_ACCENT)

        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)