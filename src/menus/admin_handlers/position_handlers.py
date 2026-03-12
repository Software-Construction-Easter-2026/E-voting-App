"""Admin menu: Position Management (Create, View, Update, Delete)."""
from src.config.constants import THEME_ADMIN, DIM, BOLD, RESET
from src.config.constants import MIN_CANDIDATE_AGE
from src.services import position_service
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminPositionHandlers(AdminHandlerBase):
    """Handles admin options 10–13: position CRUD."""

    def create_position(self) -> None:
        self.clear_screen()
        self.ui.header("CREATE POSITION", THEME_ADMIN)
        print()
        title = self.prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title:
            self.error("Title cannot be empty.")
            self.pause()
            return
        description = self.prompt("Description: ")
        level = self.prompt("Level (National/Regional/Local): ")
        try:
            max_winners = int(self.prompt("Number of winners/seats: "))
        except ValueError:
            self.error("Invalid number.")
            self.pause()
            return
        min_cand_age = self.prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
        min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else None
        ok, msg = position_service.create_position(
            self.repo, self.user["username"], title, description, level, max_winners, min_cand_age
        )
        if ok:
            self.audit.log_action("CREATE_POSITION", self.user["username"], msg)
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def view_positions(self) -> None:
        self.clear_screen()
        self.ui.header("ALL POSITIONS", THEME_ADMIN)
        if not self.repo.positions:
            print()
            self.info("No positions found.")
            self.pause()
            return
        print()
        self.ui.table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
        self.ui.table_divider(70, THEME_ADMIN)
        for pid, p in self.repo.positions.items():
            status = self.ui.status_badge("Active", True) if p["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")
        print(f"\n  {DIM}Total Positions: {len(self.repo.positions)}{RESET}")
        self.pause()

    def update_position(self) -> None:
        self.clear_screen()
        self.ui.header("UPDATE POSITION", THEME_ADMIN)
        if not self.repo.positions:
            print()
            self.info("No positions found.")
            self.pause()
            return
        print()
        for pid, p in self.repo.positions.items():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(self.prompt("\nEnter Position ID to update: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.positions:
            self.error("Position not found.")
            self.pause()
            return
        p = self.repo.positions[pid]
        print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
        self.info("Press Enter to keep current value\n")
        new_title = self.prompt(f"Title [{p['title']}]: ")
        new_desc = self.prompt(f"Description [{p['description'][:50]}]: ")
        new_level = self.prompt(f"Level [{p['level']}]: ")
        new_seats = self.prompt(f"Seats [{p['max_winners']}]: ")
        max_winners = None
        if new_seats:
            try:
                max_winners = int(new_seats)
            except ValueError:
                self.warning("Keeping old value.")
        ok, msg = position_service.update_position(
            self.repo, pid, title=new_title or None, description=new_desc or None,
            level=new_level or None, max_winners=max_winners
        )
        if ok:
            self.audit.log_action("UPDATE_POSITION", self.user["username"], f"Updated position: {p['title']}")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def delete_position(self) -> None:
        self.clear_screen()
        self.ui.header("DELETE POSITION", THEME_ADMIN)
        if not self.repo.positions:
            print()
            self.info("No positions found.")
            self.pause()
            return
        print()
        for pid, p in self.repo.positions.items():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(self.prompt("\nEnter Position ID to delete: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if pid not in self.repo.positions:
            self.error("Position not found.")
            self.pause()
            return
        if self.prompt(f"Confirm deactivation of '{self.repo.positions[pid]['title']}'? (yes/no): ").lower() != "yes":
            self.pause()
            return
        ok, msg = position_service.delete_position(self.repo, pid, self.user["username"])
        if ok:
            self.audit.log_action("DELETE_POSITION", self.user["username"], f"Deactivated position: {self.repo.positions[pid]['title']}")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()
