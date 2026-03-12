"""
Login and registration menus. Uses LoginMenu(BaseMenu) for OOP and
delegates to AuthService / AuditService for business logic.
"""
from src.config.constants import (
    THEME_LOGIN,
    THEME_ADMIN,
    THEME_VOTER,
    BRIGHT_BLUE,
    BOLD,
    BRIGHT_YELLOW,
    RESET,
    DIM,
)
from src.menus.base_menu import BaseMenu
from src.services.auth_service import AuthService
from src.services.audit_service import AuditService


class LoginMenu(BaseMenu):
    """
    First screen: login as admin, login as voter, or register as voter.
    Inherits repo and UI helpers from BaseMenu; uses AuthService and AuditService.
    """

    def __init__(self, repo):
        super().__init__(repo)
        self.auth = AuthService(repo)
        self.audit = AuditService(repo)

    def run(self) -> tuple[bool, dict]:
        """
        Show main login menu. Returns (True, session) on successful login,
        (False, None) when user exits or after failed login / registration.
        """
        self.clear_screen()
        self.ui.header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        self.ui.menu_item(1, "Login as Admin", THEME_LOGIN)
        self.ui.menu_item(2, "Login as Voter", THEME_LOGIN)
        self.ui.menu_item(3, "Register as Voter", THEME_LOGIN)
        self.ui.menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = self.prompt("Enter choice: ")

        if choice == "1":
            return self._do_admin_login()
        if choice == "2":
            return self._do_voter_login()
        if choice == "3":
            self._do_register_voter()
            return False, None
        if choice == "4":
            print()
            self.info("Goodbye!")
            ok, msg = self.repo.save()
            if ok:
                self.info(msg)
            else:
                self.error(msg)
            exit()
        self.error("Invalid choice.")
        self.pause()
        return False, None

    def _do_admin_login(self) -> tuple[bool, dict]:
        self.clear_screen()
        self.ui.header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = self.prompt("Username: ")
        password = self.ui.masked_input("Password: ").strip()
        success_flag, message, admin = self.auth.try_admin_login(username, password)
        if success_flag:
            self.audit.log_action("LOGIN", username, "Admin login successful")
            print()
            self.success(message)
            self.pause()
            return True, {"user": admin, "role": "admin"}
        self.audit.log_action("LOGIN_FAILED", username, "Invalid admin credentials" if "deactivated" not in message else "Account deactivated")
        self.error(message)
        self.pause()
        return False, None

    def _do_voter_login(self) -> tuple[bool, dict]:
        self.clear_screen()
        self.ui.header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = self.prompt("Voter Card Number: ")
        password = self.ui.masked_input("Password: ").strip()
        success_flag, message, voter = self.auth.try_voter_login(voter_card, password)
        if success_flag:
            self.audit.log_action("LOGIN", voter_card, "Voter login successful")
            print()
            self.success(message)
            self.pause()
            return True, {"user": voter, "role": "voter"}
        if message == "not_verified":
            self.audit.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
            self.warning("Your voter registration has not been verified yet.")
            self.info("Please contact an admin to verify your registration.")
        else:
            self.audit.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
            self.error(message)
        self.pause()
        return False, None

    def _do_register_voter(self) -> None:
        self.clear_screen()
        self.ui.header("VOTER REGISTRATION", THEME_VOTER)
        print()
        full_name = self.prompt("Full Name: ")
        if not full_name:
            self.error("Name cannot be empty.")
            self.pause()
            return
        national_id = self.prompt("National ID Number: ")
        dob_str = self.prompt("Date of Birth (YYYY-MM-DD): ")
        gender = self.prompt("Gender (M/F/Other): ").upper()
        address = self.prompt("Residential Address: ")
        phone = self.prompt("Phone Number: ")
        email = self.prompt("Email Address: ")
        password = self.ui.masked_input("Create Password: ").strip()
        confirm_password = self.ui.masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            self.error("Passwords do not match.")
            self.pause()
            return
        if not self.repo.voting_stations:
            self.error("No voting stations available. Contact admin.")
            self.pause()
            return
        self.ui.subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in self.repo.voting_stations.items():
            if station["is_active"]:
                print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
        try:
            station_choice = int(self.prompt("\nSelect your voting station ID: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        success_flag, message, voter_card = self.auth.register_voter(
            full_name, national_id, dob_str, gender, address, phone, email, password, station_choice
        )
        if not success_flag:
            self.error(message)
            self.pause()
            return
        self.audit.log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        print()
        self.success(message)
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
        self.warning("IMPORTANT: Save this number! You need it to login.")
        self.info("Your registration is pending admin verification.")
        ok, save_msg = self.repo.save()
        if ok:
            self.info(save_msg)
        else:
            self.error(save_msg)
        self.pause()


def run_login(repo) -> tuple[bool, dict]:
    """Entry point: run the login menu and return (logged_in, session)."""
    return LoginMenu(repo).run()
