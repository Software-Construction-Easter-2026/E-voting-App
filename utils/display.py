# All terminal display helper functions extracted from the original monolith.
# This module ONLY handles output and input prompts – zero business logic.

import os
from utils.colors import (
    RESET, BOLD, DIM, YELLOW, RED, GREEN, GRAY, BRIGHT_WHITE,
)


def colored(text, color) -> str:
    """Wrap text in an ANSI color code."""
    return f"{color}{text}{RESET}"


def header(title: str, theme_color: str) -> None:
    """Print a full-width double-border header."""
    width = 58
    print(f" {theme_color}{'═' * width}{RESET}")
    print(f" {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}")
    print(f" {theme_color}{'═' * width}{RESET}")


def subheader(title: str, theme_color: str) -> None:
    """Print an indented section subheading."""
    print(f"\n {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str: str, theme_color: str) -> None:
    """Print a bold column-header row."""
    print(f" {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width: int, theme_color: str) -> None:
    """Print a horizontal table divider of given width."""
    print(f" {theme_color}{'─' * width}{RESET}")


def error(msg: str) -> None:
    """Print an error message."""
    print(f" {RED}{BOLD} {msg}{RESET}")


def success(msg: str) -> None:
    """Print a success message."""
    print(f" {GREEN}{BOLD} {msg}{RESET}")


def warning(msg: str) -> None:
    """Print a warning message."""
    print(f" {YELLOW}{BOLD} {msg}{RESET}")


def info(msg: str) -> None:
    """Print an informational message."""
    print(f" {GRAY}{msg}{RESET}")


def menu_item(number: int, text: str, color: str) -> None:
    """Print a formatted menu item."""
    print(f" {color}{BOLD}{number:>3}.{RESET} {text}")


def status_badge(text: str, is_good: bool) -> str:
    """Return a colored badge showing status."""
    return f"{GREEN}{text}{RESET}" if is_good else f"{RED}{text}{RESET}"


def prompt(text: str) -> str:
    """Show a styled input prompt and return user input."""
    return input(f" {BRIGHT_WHITE}{text}{RESET}").strip()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Pause execution until the user presses Enter."""
    input(f"\n {DIM}Press Enter to continue...{RESET}")