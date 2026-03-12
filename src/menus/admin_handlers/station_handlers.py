"""Admin menu: Voting Station Management (Create, View, Update, Delete)."""
from src.config.constants import THEME_ADMIN, DIM, BOLD, RESET
from src.services import station_service
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminStationHandlers(AdminHandlerBase):
    """Handles admin options 6–9: station CRUD."""

    def create_station(self) -> None:
        self.clear_screen()
        self.ui.header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name = self.prompt("Station Name: ")
        if not name:
            self.error("Name cannot be empty.")
            self.pause()
            return
        location = self.prompt("Location/Address: ")
        if not location:
            self.error("Location cannot be empty.")
            self.pause()
            return
        region = self.prompt("Region/District: ")
        try:
            capacity = int(self.prompt("Voter Capacity: "))
        except ValueError:
            self.error("Invalid capacity.")
            self.pause()
            return
        supervisor = self.prompt("Station Supervisor Name: ")
        contact = self.prompt("Contact Phone: ")
        opening_time = self.prompt("Opening Time (e.g. 08:00): ")
        closing_time = self.prompt("Closing Time (e.g. 17:00): ")
        ok, msg = station_service.create_station(
            self.repo, self.user["username"], name, location, region, capacity,
            supervisor, contact, opening_time, closing_time
        )
        if ok:
            self.audit.log_action("CREATE_STATION", self.user["username"], msg)
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def view_all_stations(self) -> None:
        self.clear_screen()
        self.ui.header("ALL VOTING STATIONS", THEME_ADMIN)
        if not self.repo.voting_stations:
            print()
            self.info("No voting stations found.")
            self.pause()
            return
        print()
        self.ui.table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
        self.ui.table_divider(96, THEME_ADMIN)
        for sid, s in self.repo.voting_stations.items():
            reg_count = station_service.count_registered_at_station(self.repo, sid)
            status = self.ui.status_badge("Active", True) if s["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")
        print(f"\n  {DIM}Total Stations: {len(self.repo.voting_stations)}{RESET}")
        self.pause()

    def update_station(self) -> None:
        self.clear_screen()
        self.ui.header("UPDATE VOTING STATION", THEME_ADMIN)
        if not self.repo.voting_stations:
            print()
            self.info("No stations found.")
            self.pause()
            return
        print()
        for sid, s in self.repo.voting_stations.items():
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
        try:
            sid = int(self.prompt("\nEnter Station ID to update: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if sid not in self.repo.voting_stations:
            self.error("Station not found.")
            self.pause()
            return
        s = self.repo.voting_stations[sid]
        print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
        self.info("Press Enter to keep current value\n")
        new_name = self.prompt(f"Name [{s['name']}]: ")
        new_location = self.prompt(f"Location [{s['location']}]: ")
        new_region = self.prompt(f"Region [{s['region']}]: ")
        new_capacity = self.prompt(f"Capacity [{s['capacity']}]: ")
        capacity = None
        if new_capacity:
            try:
                capacity = int(new_capacity)
            except ValueError:
                self.warning("Invalid number, keeping old value.")
        new_supervisor = self.prompt(f"Supervisor [{s['supervisor']}]: ")
        new_contact = self.prompt(f"Contact [{s['contact']}]: ")
        ok, msg = station_service.update_station(
            self.repo, sid, name=new_name or None, location=new_location or None, region=new_region or None,
            capacity=capacity, supervisor=new_supervisor or None, contact=new_contact or None
        )
        if ok:
            self.audit.log_action("UPDATE_STATION", self.user["username"], f"Updated station: {s['name']} (ID: {sid})")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def delete_station(self) -> None:
        self.clear_screen()
        self.ui.header("DELETE VOTING STATION", THEME_ADMIN)
        if not self.repo.voting_stations:
            print()
            self.info("No stations found.")
            self.pause()
            return
        print()
        for sid, s in self.repo.voting_stations.items():
            status = self.ui.status_badge("Active", True) if s["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
        try:
            sid = int(self.prompt("\nEnter Station ID to delete: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if sid not in self.repo.voting_stations:
            self.error("Station not found.")
            self.pause()
            return
        voter_count = station_service.count_registered_at_station(self.repo, sid)
        if voter_count > 0:
            self.warning(f"{voter_count} voters are registered at this station.")
            if self.prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                self.info("Cancelled.")
                self.pause()
                return
        if self.prompt(f"Confirm deactivation of '{self.repo.voting_stations[sid]['name']}'? (yes/no): ").lower() != "yes":
            self.info("Cancelled.")
            self.pause()
            return
        ok, msg = station_service.delete_station(self.repo, sid, self.user["username"])
        if ok:
            self.audit.log_action("DELETE_STATION", self.user["username"], f"Deactivated station: {self.repo.voting_stations[sid]['name']}")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()
