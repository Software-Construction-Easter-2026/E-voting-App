
# All terminal display helper functions extracted from the original monolith.
# This module ONLY handles output and input prompts – zero business logic.

import os
import sys
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
    print(f" {RED}{BOLD} {msg}{RESET}")


def success(msg: str) -> None:
    print(f" {GREEN}{BOLD} {msg}{RESET}")


def warning(msg: str) -> None:
    print(f" {YELLOW}{BOLD} {msg}{RESET}")


def info(msg: str) -> None:
    print(f" {GRAY}{msg}{RESET}")


def menu_item(number: int, text: str, color: str) -> None:
    print(f" {color}{BOLD}{number:>3}.{RESET} {text}")


def status_badge(text: str, is_good: bool) -> str:
    """Return a colored inline badge (does NOT print)."""
    return f"{GREEN}{text}{RESET}" if is_good else f"{RED}{text}{RESET}"


def prompt(text: str) -> str:
    """Show a styled input prompt and return stripped user input."""
    return input(f" {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text: str = "Password: ") -> str:
    """Read a password character-by-character, echoing '*' instead of the real char."""
    print(f" {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print()
                    break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input(f"\n {DIM}Press Enter to continue...{RESET}")
