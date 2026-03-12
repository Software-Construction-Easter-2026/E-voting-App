"""
Admin menu handler classes. Each class handles one section of the admin dashboard
(Candidates, Stations, Positions, Polls, Voters, Admin accounts, Results/Audit).
AdminMenu composes these via inheritance of BaseMenu and delegation to handlers.
"""
from src.menus.admin_handlers.candidate_handlers import AdminCandidateHandlers
from src.menus.admin_handlers.station_handlers import AdminStationHandlers
from src.menus.admin_handlers.position_handlers import AdminPositionHandlers
from src.menus.admin_handlers.poll_handlers import AdminPollHandlers
from src.menus.admin_handlers.voter_handlers import AdminVoterHandlers
from src.menus.admin_handlers.account_handlers import AdminAccountHandlers
from src.menus.admin_handlers.results_handlers import AdminResultsHandlers

__all__ = [
    "AdminCandidateHandlers",
    "AdminStationHandlers",
    "AdminPositionHandlers",
    "AdminPollHandlers",
    "AdminVoterHandlers",
    "AdminAccountHandlers",
    "AdminResultsHandlers",
]
