"""
Base class for all menu controllers. Provides common behaviour (repo, UI helpers)
so that LoginMenu, AdminMenu, and VoterMenu can inherit and avoid duplication.
"""
from src.data.repository import Repository
from src.ui import console as ui


class BaseMenu:
    """
    Abstract base for menu controllers. Holds the repository and exposes
    common UI operations so subclasses only implement their specific flow.
    """

    def __init__(self, repo: Repository):
        self.repo = repo
        self.ui = ui

    def clear_screen(self) -> None:
        """Clear the terminal."""
        self.ui.clear_screen()

    def pause(self) -> None:
        """Wait for Enter."""
        self.ui.pause()

    def prompt(self, text: str) -> str:
        """Read one line of input."""
        return self.ui.prompt(text)

    def success(self, msg: str) -> None:
        self.ui.success(msg)

    def error(self, msg: str) -> None:
        self.ui.error(msg)

    def warning(self, msg: str) -> None:
        self.ui.warning(msg)

    def info(self, msg: str) -> None:
        self.ui.info(msg)
