"""
Base class for all service classes. Holds the repository so each service
encapsulates access to data and exposes only domain operations.
"""
from src.data.repository import Repository


class BaseService:
    """
    Base for business-logic services. Subclasses get the repository
    via constructor and implement domain-specific methods (create, update, etc.).
    """

    def __init__(self, repo: Repository):
        self.repo = repo
