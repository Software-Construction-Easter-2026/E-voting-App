"""
Base class for admin dashboard handler classes. Inherits from BaseMenu (repo + UI helpers)
and adds session (current user) and shared AuditService so each handler has one responsibility.
"""
from src.menus.base_menu import BaseMenu
from src.services.audit_service import AuditService


class AdminHandlerBase(BaseMenu):
    """
    Base for admin section handlers (candidates, stations, polls, etc.).
    Subclasses get repo, session, ui, and audit service; each implements
    only its own menu actions (e.g. create_candidate, view_all_candidates).
    """

    def __init__(self, repo, session: dict):
        super().__init__(repo)
        self.session = session
        self.user = session["user"]
        self.audit = AuditService(repo)
