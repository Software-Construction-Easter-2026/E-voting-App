"""Admin menu: Voter management (View all, Verify, Deactivate, Search)."""
from src.config.constants import THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, BOLD, RESET
from src.services import voter_service
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminVoterHandlers(AdminHandlerBase):
    """Handles admin options 20–23: voter view, verify, deactivate, search."""

    def view_all_voters(self) -> None:
        self.clear_screen()
        self.ui.header("ALL REGISTERED VOTERS", THEME_ADMIN)
        if not self.repo.voters:
            print()
            self.info("No voters registered.")
            self.pause()
            return
        print()
        self.ui.table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN,
        )
        self.ui.table_divider(70, THEME_ADMIN)
        for vid, v in self.repo.voters.items():
            verified = self.ui.status_badge("Yes", True) if v["is_verified"] else self.ui.status_badge("No", False)
            active = self.ui.status_badge("Yes", True) if v["is_active"] else self.ui.status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
        verified_count = sum(1 for v in self.repo.voters.values() if v["is_verified"])
        unverified_count = sum(1 for v in self.repo.voters.values() if not v["is_verified"])
        print(f"\n  {DIM}Total: {len(self.repo.voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        self.pause()

    def verify_voter(self) -> None:
        self.clear_screen()
        self.ui.header("VERIFY VOTER", THEME_ADMIN)
        unverified = {vid: v for vid, v in self.repo.voters.items() if not v["is_verified"]}
        if not unverified:
            print()
            self.info("No unverified voters.")
            self.pause()
            return
        self.ui.subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for vid, v in unverified.items():
            print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
        print()
        self.ui.menu_item(1, "Verify a single voter", THEME_ADMIN)
        self.ui.menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = self.prompt("\nChoice: ")
        if choice == "1":
            try:
                vid = int(self.prompt("Enter Voter ID: "))
            except ValueError:
                self.error("Invalid input.")
                self.pause()
                return
            ok, msg = voter_service.verify_voter(self.repo, vid, self.user["username"])
            if ok:
                self.audit.log_action("VERIFY_VOTER", self.user["username"], msg)
                self.success(msg)
                self.repo.save()
            else:
                self.error(msg)
        elif choice == "2":
            ok, msg, count = voter_service.verify_all_pending(self.repo, self.user["username"])
            if ok and count > 0:
                self.audit.log_action("VERIFY_ALL_VOTERS", self.user["username"], msg)
                self.success(msg)
                self.repo.save()
            elif ok:
                self.info("No unverified voters.")
            else:
                self.error(msg)
        else:
            self.error("Invalid choice.")
        self.pause()

    def deactivate_voter(self) -> None:
        self.clear_screen()
        self.ui.header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self.repo.voters:
            print()
            self.info("No voters found.")
            self.pause()
            return
        print()
        try:
            vid = int(self.prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if vid not in self.repo.voters:
            self.error("Voter not found.")
            self.pause()
            return
        if not self.repo.voters[vid]["is_active"]:
            self.info("Already deactivated.")
            self.pause()
            return
        if self.prompt(f"Deactivate '{self.repo.voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
            ok, msg = voter_service.deactivate_voter(self.repo, vid, self.user["username"])
            if ok:
                self.audit.log_action("DEACTIVATE_VOTER", self.user["username"], msg)
                self.success("Voter deactivated.")
                self.repo.save()
            else:
                self.error(msg)
        self.pause()

    def search_voters(self) -> None:
        self.clear_screen()
        self.ui.header("SEARCH VOTERS", THEME_ADMIN)
        self.ui.subheader("Search by", THEME_ADMIN_ACCENT)
        self.ui.menu_item(1, "Name", THEME_ADMIN)
        self.ui.menu_item(2, "Voter Card Number", THEME_ADMIN)
        self.ui.menu_item(3, "National ID", THEME_ADMIN)
        self.ui.menu_item(4, "Station", THEME_ADMIN)
        choice = self.prompt("\nChoice: ")
        results = []
        if choice == "1":
            term = self.prompt("Name: ").lower()
            results = voter_service.search_voters_by_name(self.repo, term)
        elif choice == "2":
            term = self.prompt("Card Number: ")
            results = voter_service.search_voters_by_card(self.repo, term)
        elif choice == "3":
            term = self.prompt("National ID: ")
            results = voter_service.search_voters_by_national_id(self.repo, term)
        elif choice == "4":
            try:
                sid = int(self.prompt("Station ID: "))
                results = voter_service.search_voters_by_station(self.repo, sid)
            except ValueError:
                self.error("Invalid input.")
                self.pause()
                return
        else:
            self.error("Invalid choice.")
            self.pause()
            return
        if not results:
            print()
            self.info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = self.ui.status_badge("Verified", True) if v["is_verified"] else self.ui.status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
        self.pause()
