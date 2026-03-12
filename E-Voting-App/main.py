"""
National E-Voting Console Application — Entry point.
Refactored for Software Construction (Year 3, 2) — Easter 2026 Semester Test.
Run this file to start the application. Behaviour matches the original monolith.
"""
import time

from src.config.constants import THEME_LOGIN, RESET
from src.data.repository import Repository
from src.ui import console as ui
from src.menus import login_menu
from src.menus import admin_menu
from src.menus import voter_menu


def main() -> None:
    """Load data, then run login loop; on success run admin or voter dashboard."""
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    repo = Repository()
    ok, msg = repo.load()
    if ok:
        ui.info(msg)
    else:
        ui.error(msg)
    time.sleep(1)
    while True:
        logged_in, session = login_menu.run_login(repo)
        if logged_in and session:
            if session["role"] == "admin":
                admin_menu.run_admin_dashboard(repo, session)
            elif session["role"] == "voter":
                voter_menu.run_voter_dashboard(repo, session)


if __name__ == "__main__":
    main()
