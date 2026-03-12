"""Console UI: colors, headers, menus, prompts, and display helpers."""

import os
import sys

from .themes import (
    BOLD,
    DIM,
    GRAY,
    GREEN,
    RED,
    RESET,
    YELLOW,
    BRIGHT_WHITE,
)


def colored(text, color):
    return f"{color}{text}{RESET}"


def header(title, theme_color):
    """Print main section header."""
    width = 58
    border = f"{theme_color}{'═' * width}{RESET}"

    print(f"  {border}")
    print(f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}")
    print(f"  {border}")


def subheader(title, theme_color):
    """Print subsection header."""
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    """Print formatted table header."""
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    """Print divider for tables."""
    print(f"  {theme_color}{'─' * width}{RESET}")


def error(msg):
    print(f"  {RED}{BOLD}{msg}{RESET}")


def success(msg):
    print(f"  {GREEN}{BOLD}{msg}{RESET}")


def warning(msg):
    print(f"  {YELLOW}{BOLD}{msg}{RESET}")


def info(msg):
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number, text, color):
    """Print menu option."""
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    """Return colored status label."""
    color = GREEN if is_good else RED
    return f"{color}{text}{RESET}"


def prompt(text):
    """Prompt user for input."""
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def prompt_until_valid(prompt_text, validator, optional=False):
    """
    Prompt user until validator returns (True, "").
    validator: function(value) -> (bool, error_message)
    """
    while True:
        value = prompt(prompt_text)

        if optional and value == "":
            return ""

        ok, err = validator(value)

        if ok:
            return value

        error(err)


def masked_input(prompt_text="Password: "):
    """Password input with masking."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)

    password = ""

    if sys.platform == "win32":
        import msvcrt

        while True:
            ch = msvcrt.getwch()

            if ch in ("\r", "\n"):
                print()
                break

            if ch in ("\x08", "\b"):
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

                if ch in ("\x7f", "\x08"):
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


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    """Pause execution until user presses Enter."""
    input(f"\n  {DIM}Press Enter to continue...{RESET}")