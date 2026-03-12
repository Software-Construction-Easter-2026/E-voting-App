"""Admin menu: Admin account management (Create, View, Deactivate)."""
from src.config.constants import THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, RESET
from src.services import admin_service
from src.menus.admin_handlers.base import AdminHandlerBase


class AdminAccountHandlers(AdminHandlerBase):
    """Handles admin options 24–26: create admin, view admins, deactivate admin."""

    def create_admin(self) -> None:
        self.clear_screen()
        self.ui.header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if self.user["role"] != "super_admin":
            print()
            self.error("Only super admins can create admin accounts.")
            self.pause()
            return
        print()
        username = self.prompt("Username: ")
        if not username:
            self.error("Username cannot be empty.")
            self.pause()
            return
        full_name = self.prompt("Full Name: ")
        email = self.prompt("Email: ")
        password = self.ui.masked_input("Password: ").strip()
        if len(password) < 6:
            self.error("Password must be at least 6 characters.")
            self.pause()
            return
        self.ui.subheader("Available Roles", THEME_ADMIN_ACCENT)
        self.ui.menu_item(1, f"super_admin {DIM}─ Full access{RESET}", THEME_ADMIN)
        self.ui.menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}", THEME_ADMIN)
        self.ui.menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
        self.ui.menu_item(4, f"auditor {DIM}─ Read-only access{RESET}", THEME_ADMIN)
        role_choice = self.prompt("\nSelect role (1-4): ")
        role_map = {"1": "super_admin", "2": "election_officer", "3": "station_manager", "4": "auditor"}
        if role_choice not in role_map:
            self.error("Invalid role.")
            self.pause()
            return
        role = role_map[role_choice]
        ok, msg = admin_service.create_admin(
            self.repo, self.user["username"], username, full_name, email, password, role
        )
        if ok:
            self.audit.log_action("CREATE_ADMIN", self.user["username"], f"Created admin: {username} (Role: {role})")
            self.success(msg)
            self.repo.save()
        else:
            self.error(msg)
        self.pause()

    def view_admins(self) -> None:
        self.clear_screen()
        self.ui.header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        self.ui.table_header(
            f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
            THEME_ADMIN,
        )
        self.ui.table_divider(78, THEME_ADMIN)
        for aid, a in self.repo.admins.items():
            active = self.ui.status_badge("Yes", True) if a["is_active"] else self.ui.status_badge("No", False)
            print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
        print(f"\n  {DIM}Total Admins: {len(self.repo.admins)}{RESET}")
        self.pause()

    def deactivate_admin(self) -> None:
        self.clear_screen()
        self.ui.header("DEACTIVATE ADMIN", THEME_ADMIN)
        if self.user["role"] != "super_admin":
            print()
            self.error("Only super admins can deactivate admins.")
            self.pause()
            return
        print()
        for aid, a in self.repo.admins.items():
            active = self.ui.status_badge("Active", True) if a["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
        try:
            aid = int(self.prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            self.error("Invalid input.")
            self.pause()
            return
        if aid not in self.repo.admins:
            self.error("Admin not found.")
            self.pause()
            return
        if aid == self.user["id"]:
            self.error("Cannot deactivate your own account.")
            self.pause()
            return
        if self.prompt(f"Deactivate '{self.repo.admins[aid]['username']}'? (yes/no): ").lower() == "yes":
            ok, msg = admin_service.deactivate_admin(
                self.repo, aid, self.user["id"], self.user["username"]
            )
            if ok:
                self.audit.log_action("DEACTIVATE_ADMIN", self.user["username"], f"Deactivated admin: {self.repo.admins[aid]['username']}")
                self.success("Admin deactivated.")
                self.repo.save()
            else:
                self.error(msg)
        self.pause()
