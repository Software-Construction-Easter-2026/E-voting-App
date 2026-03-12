"""
Admin dashboard: menu loop and dispatch to handler classes.
AdminMenu(BaseMenu) uses composition: each handler class owns one section (Candidates, Stations, etc.).
No single file exceeds ~250 lines; OOP and single responsibility are preserved.
"""
from src.config.constants import (
    THEME_ADMIN,
    THEME_ADMIN_ACCENT,
    DIM,
    BOLD,
    RESET,
)
from src.menus.base_menu import BaseMenu
from src.menus.admin_handlers import (
    AdminCandidateHandlers,
    AdminStationHandlers,
    AdminPositionHandlers,
    AdminPollHandlers,
    AdminVoterHandlers,
    AdminAccountHandlers,
    AdminResultsHandlers,
)
from src.services.audit_service import AuditService


class AdminMenu(BaseMenu):
    """
    Admin dashboard: displays the 32-option menu and delegates each action
    to the appropriate handler class (Candidates, Stations, Positions, Polls,
    Voters, Admin accounts, Results/Audit). Inherits repo and UI from BaseMenu.
    """

    def __init__(self, repo, session: dict):
        super().__init__(repo)
        self.session = session
        self.user = session["user"]
        self.audit = AuditService(repo)
        # Composition: each handler is responsible for its own section
        self.candidate = AdminCandidateHandlers(repo, session)
        self.station = AdminStationHandlers(repo, session)
        self.position = AdminPositionHandlers(repo, session)
        self.poll = AdminPollHandlers(repo, session)
        self.voter = AdminVoterHandlers(repo, session)
        self.account = AdminAccountHandlers(repo, session)
        self.results = AdminResultsHandlers(repo, session)

    def run(self) -> None:
        """Main admin loop: show menu and dispatch to handlers until logout."""
        while True:
            self.clear_screen()
            self.ui.header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{self.user['full_name']}{RESET}  {DIM}│  Role: {self.user['role']}{RESET}")

            self.ui.subheader("Candidate Management", THEME_ADMIN_ACCENT)
            self.ui.menu_item(1, "Create Candidate", THEME_ADMIN)
            self.ui.menu_item(2, "View All Candidates", THEME_ADMIN)
            self.ui.menu_item(3, "Update Candidate", THEME_ADMIN)
            self.ui.menu_item(4, "Delete Candidate", THEME_ADMIN)
            self.ui.menu_item(5, "Search Candidates", THEME_ADMIN)
            self.ui.subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            self.ui.menu_item(6, "Create Voting Station", THEME_ADMIN)
            self.ui.menu_item(7, "View All Stations", THEME_ADMIN)
            self.ui.menu_item(8, "Update Station", THEME_ADMIN)
            self.ui.menu_item(9, "Delete Station", THEME_ADMIN)
            self.ui.subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            self.ui.menu_item(10, "Create Position", THEME_ADMIN)
            self.ui.menu_item(11, "View Positions", THEME_ADMIN)
            self.ui.menu_item(12, "Update Position", THEME_ADMIN)
            self.ui.menu_item(13, "Delete Position", THEME_ADMIN)
            self.ui.menu_item(14, "Create Poll", THEME_ADMIN)
            self.ui.menu_item(15, "View All Polls", THEME_ADMIN)
            self.ui.menu_item(16, "Update Poll", THEME_ADMIN)
            self.ui.menu_item(17, "Delete Poll", THEME_ADMIN)
            self.ui.menu_item(18, "Open/Close Poll", THEME_ADMIN)
            self.ui.menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)
            self.ui.subheader("Voter Management", THEME_ADMIN_ACCENT)
            self.ui.menu_item(20, "View All Voters", THEME_ADMIN)
            self.ui.menu_item(21, "Verify Voter", THEME_ADMIN)
            self.ui.menu_item(22, "Deactivate Voter", THEME_ADMIN)
            self.ui.menu_item(23, "Search Voters", THEME_ADMIN)
            self.ui.subheader("Admin Management", THEME_ADMIN_ACCENT)
            self.ui.menu_item(24, "Create Admin Account", THEME_ADMIN)
            self.ui.menu_item(25, "View Admins", THEME_ADMIN)
            self.ui.menu_item(26, "Deactivate Admin", THEME_ADMIN)
            self.ui.subheader("Results & Reports", THEME_ADMIN_ACCENT)
            self.ui.menu_item(27, "View Poll Results", THEME_ADMIN)
            self.ui.menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            self.ui.menu_item(29, "View Audit Log", THEME_ADMIN)
            self.ui.menu_item(30, "Station-wise Results", THEME_ADMIN)
            self.ui.subheader("System", THEME_ADMIN_ACCENT)
            self.ui.menu_item(31, "Save Data", THEME_ADMIN)
            self.ui.menu_item(32, "Logout", THEME_ADMIN)
            print()
            choice = self.prompt("Enter choice: ")

            if choice == "1":
                self.candidate.create_candidate()
            elif choice == "2":
                self.candidate.view_all_candidates()
            elif choice == "3":
                self.candidate.update_candidate()
            elif choice == "4":
                self.candidate.delete_candidate()
            elif choice == "5":
                self.candidate.search_candidates()
            elif choice == "6":
                self.station.create_station()
            elif choice == "7":
                self.station.view_all_stations()
            elif choice == "8":
                self.station.update_station()
            elif choice == "9":
                self.station.delete_station()
            elif choice == "10":
                self.position.create_position()
            elif choice == "11":
                self.position.view_positions()
            elif choice == "12":
                self.position.update_position()
            elif choice == "13":
                self.position.delete_position()
            elif choice == "14":
                self.poll.create_poll()
            elif choice == "15":
                self.poll.view_all_polls()
            elif choice == "16":
                self.poll.update_poll()
            elif choice == "17":
                self.poll.delete_poll()
            elif choice == "18":
                self.poll.open_close_poll()
            elif choice == "19":
                self.poll.assign_candidates_to_poll()
            elif choice == "20":
                self.voter.view_all_voters()
            elif choice == "21":
                self.voter.verify_voter()
            elif choice == "22":
                self.voter.deactivate_voter()
            elif choice == "23":
                self.voter.search_voters()
            elif choice == "24":
                self.account.create_admin()
            elif choice == "25":
                self.account.view_admins()
            elif choice == "26":
                self.account.deactivate_admin()
            elif choice == "27":
                self.results.view_poll_results()
            elif choice == "28":
                self.results.view_detailed_statistics()
            elif choice == "29":
                self.results.view_audit_log()
            elif choice == "30":
                self.results.station_wise_results()
            elif choice == "31":
                ok, msg = self.repo.save()
                if ok:
                    self.info(msg)
                else:
                    self.error(msg)
                self.pause()
            elif choice == "32":
                self.audit.log_action("LOGOUT", self.user["username"], "Admin logged out")
                self.repo.save()
                break
            else:
                self.error("Invalid choice.")
                self.pause()


def run_admin_dashboard(repo, session: dict) -> None:
    """Entry point: run the admin menu (delegates to AdminMenu class)."""
    AdminMenu(repo, session).run()
