import time

from evoting.app_context import AppContext
from evoting.core.colors import RESET, THEME_LOGIN
from evoting.data.repository import Repository
from evoting.menus.admin_menu import run_admin_dashboard
from evoting.menus.login_menu import run_login
from evoting.menus.voter_menu import run_voter_dashboard
from evoting.services.audit_service import AuditService
from evoting.services.auth_service import AuthService
from evoting.services.candidate_service import CandidateService
from evoting.services.station_service import StationService
from evoting.services.position_service import PositionService
from evoting.services.poll_service import PollService
from evoting.services.voter_service import VoterService
from evoting.services.admin_service import AdminService
from evoting.services.vote_service import VoteService
from evoting.services.results_service import ResultsService
from evoting.ui.console_io import clear_screen, init_console
from evoting.ui import display


def main():
    init_console()
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    repo = Repository()
    try:
        repo.load()
        display.info("Data loaded successfully")
    except Exception as e:
        display.error(f"Error loading data: {e}")
    time.sleep(1)

    audit = AuditService(repo)
    auth = AuthService(repo, audit)
    candidate_svc = CandidateService(repo, audit)
    station_svc = StationService(repo, audit)
    position_svc = PositionService(repo, audit)
    poll_svc = PollService(repo, audit)
    voter_svc = VoterService(repo, audit)
    admin_svc = AdminService(repo, audit, auth)
    vote_svc = VoteService(repo, audit, voter_svc, auth)
    results_svc = ResultsService(repo)

    ctx = AppContext(
        repo=repo,
        auth=auth,
        candidate_svc=candidate_svc,
        station_svc=station_svc,
        position_svc=position_svc,
        poll_svc=poll_svc,
        voter_svc=voter_svc,
        admin_svc=admin_svc,
        vote_svc=vote_svc,
        results_svc=results_svc,
    )

    while True:
        clear_screen()
        try:
            logged_in = run_login(repo, auth)
        except SystemExit:
            break
        if logged_in:
            if auth.current_role == "admin":
                run_admin_dashboard(ctx)
            elif auth.current_role == "voter":
                run_voter_dashboard(ctx)
            auth.current_user = None
            auth.current_role = None


if __name__ == "__main__":
    main()
