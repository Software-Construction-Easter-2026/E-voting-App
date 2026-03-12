from evoting.core.colors import BOLD, DIM, RESET, THEME_ADMIN, THEME_ADMIN_ACCENT
from evoting.ui import console_io, display

from evoting.menus import admin_handlers, admin_handlers_extra


def run_admin_dashboard(ctx):
    while True:
        console_io.clear_screen()
        display.header("ADMIN DASHBOARD", THEME_ADMIN)
        print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{ctx.auth.current_user['full_name']}{RESET}  {DIM}│  Role: {ctx.auth.current_user['role']}{RESET}")

        display.subheader("Candidate Management", THEME_ADMIN_ACCENT)
        display.menu_item(1, "Create Candidate", THEME_ADMIN)
        display.menu_item(2, "View All Candidates", THEME_ADMIN)
        display.menu_item(3, "Update Candidate", THEME_ADMIN)
        display.menu_item(4, "Delete Candidate", THEME_ADMIN)
        display.menu_item(5, "Search Candidates", THEME_ADMIN)

        display.subheader("Voting Station Management", THEME_ADMIN_ACCENT)
        display.menu_item(6, "Create Voting Station", THEME_ADMIN)
        display.menu_item(7, "View All Stations", THEME_ADMIN)
        display.menu_item(8, "Update Station", THEME_ADMIN)
        display.menu_item(9, "Delete Station", THEME_ADMIN)

        display.subheader("Polls & Positions", THEME_ADMIN_ACCENT)
        display.menu_item(10, "Create Position", THEME_ADMIN)
        display.menu_item(11, "View Positions", THEME_ADMIN)
        display.menu_item(12, "Update Position", THEME_ADMIN)
        display.menu_item(13, "Delete Position", THEME_ADMIN)
        display.menu_item(14, "Create Poll", THEME_ADMIN)
        display.menu_item(15, "View All Polls", THEME_ADMIN)
        display.menu_item(16, "Update Poll", THEME_ADMIN)
        display.menu_item(17, "Delete Poll", THEME_ADMIN)
        display.menu_item(18, "Open/Close Poll", THEME_ADMIN)
        display.menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

        display.subheader("Voter Management", THEME_ADMIN_ACCENT)
        display.menu_item(20, "View All Voters", THEME_ADMIN)
        display.menu_item(21, "Verify Voter", THEME_ADMIN)
        display.menu_item(22, "Deactivate Voter", THEME_ADMIN)
        display.menu_item(23, "Search Voters", THEME_ADMIN)

        display.subheader("Admin Management", THEME_ADMIN_ACCENT)
        display.menu_item(24, "Create Admin Account", THEME_ADMIN)
        display.menu_item(25, "View Admins", THEME_ADMIN)
        display.menu_item(26, "Deactivate Admin", THEME_ADMIN)

        display.subheader("Results & Reports", THEME_ADMIN_ACCENT)
        display.menu_item(27, "View Poll Results", THEME_ADMIN)
        display.menu_item(28, "View Detailed Statistics", THEME_ADMIN)
        display.menu_item(29, "View Audit Log", THEME_ADMIN)
        display.menu_item(30, "Station-wise Results", THEME_ADMIN)

        display.subheader("System", THEME_ADMIN_ACCENT)
        display.menu_item(31, "Save Data", THEME_ADMIN)
        display.menu_item(32, "Logout", THEME_ADMIN)
        print()
        choice = console_io.prompt("Enter choice: ")

        handlers = {
            "1": admin_handlers.create_candidate,
            "2": admin_handlers.view_all_candidates,
            "3": admin_handlers.update_candidate,
            "4": admin_handlers.delete_candidate,
            "5": admin_handlers.search_candidates,
            "6": admin_handlers.create_voting_station,
            "7": admin_handlers.view_all_stations,
            "8": admin_handlers.update_station,
            "9": admin_handlers.delete_station,
            "10": admin_handlers.create_position,
            "11": admin_handlers.view_positions,
            "12": admin_handlers.update_position,
            "13": admin_handlers.delete_position,
            "14": admin_handlers.create_poll,
            "15": admin_handlers.view_all_polls,
            "16": admin_handlers.update_poll,
            "17": admin_handlers.delete_poll,
            "18": admin_handlers.open_close_poll,
            "19": admin_handlers_extra.assign_candidates_to_poll,
            "20": admin_handlers_extra.view_all_voters,
            "21": admin_handlers_extra.verify_voter,
            "22": admin_handlers_extra.deactivate_voter,
            "23": admin_handlers_extra.search_voters,
            "24": admin_handlers_extra.create_admin,
            "25": admin_handlers_extra.view_admins,
            "26": admin_handlers_extra.deactivate_admin,
            "27": admin_handlers_extra.view_poll_results,
            "28": admin_handlers_extra.view_detailed_statistics,
            "29": admin_handlers_extra.view_audit_log,
            "30": admin_handlers_extra.station_wise_results,
        }
        if choice == "31":
            try:
                ctx.repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
            console_io.pause()
        elif choice == "32":
            ctx.auth.logout()
            try:
                ctx.repo.save()
                display.info("Data saved successfully")
            except Exception as e:
                display.error(f"Error saving data: {e}")
            break
        elif choice in handlers:
            handlers[choice](ctx)
        else:
            display.error("Invalid choice.")
            console_io.pause()
