#!/usr/bin/env python3
"""
Run from this directory: python e_voting_console_app.py
Or from repo root: python refactored/e_voting_console_app.py
"""
import os
import sys
import time

# Ensure the refactored directory is on the path so that 'ui', 'services', 'data', 'app', 'models' resolve
_REFACTORED_DIR = os.path.dirname(os.path.abspath(__file__))
if _REFACTORED_DIR not in sys.path:
    sys.path.insert(0, _REFACTORED_DIR)

# Use refactored directory as cwd for data file (evoting_data.json)
os.chdir(_REFACTORED_DIR)

if sys.platform == "win32":
    os.system("")

from ui.themes import THEME_LOGIN, RESET
from ui import console
from data.context import DataContext
from app.login_flow import run as run_login
from app.admin_dashboard import run as run_admin_dashboard
from app.voter_dashboard import run as run_voter_dashboard
from services import auth_service


def main():
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    ctx = DataContext()
    ok, err = ctx.store.load()
    if not ok:
        console.error(f"Error loading data: {err}")
    elif err != "no_file":
        console.info("Data loaded successfully")
    time.sleep(1)
    while True:
        logged_in, should_exit = run_login(ctx)
        if should_exit:
            break
        if logged_in:
            if auth_service.current_role == "admin":
                run_admin_dashboard(ctx)
            elif auth_service.current_role == "voter":
                run_voter_dashboard(ctx)
            auth_service.clear_session()


if __name__ == "__main__":
    main()
