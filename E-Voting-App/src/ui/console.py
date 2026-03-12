"""
Console UI: colours, headers, prompts, and display helpers.

Everything that appears on the terminal or is read from the user goes through
this module. It does not know about candidates, polls, or votes—only how to
print a header, show an error in red, ask for a password with masked input,
etc. This keeps the look and feel in one place and lets the rest of the app
focus on logic and data.
"""
import os
import sys

from src.config import constants as C

# Enable ANSI colors on Windows
if sys.platform == "win32":
    os.system("")


def colored(text: str, color: str) -> str:
    """Wrap text with ANSI color and reset."""
    return f"{color}{text}{C.RESET}"


def header(title: str, theme_color: str) -> None:
    """Print a boxed header with the given title and color."""
    width = 58
    top = f"  {theme_color}{'═' * width}{C.RESET}"
    mid = f"  {theme_color}{C.BOLD} {title.center(width - 2)} {C.RESET}{theme_color} {C.RESET}"
    bot = f"  {theme_color}{'═' * width}{C.RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title: str, theme_color: str) -> None:
    """Print a subheading with arrow."""
    print(f"\n  {theme_color}{C.BOLD}▸ {title}{C.RESET}")


def table_header(format_str: str, theme_color: str) -> None:
    """Print a bold table header line."""
    print(f"  {theme_color}{C.BOLD}{format_str}{C.RESET}")


def table_divider(width: int, theme_color: str) -> None:
    """Print a horizontal divider line."""
    print(f"  {theme_color}{'─' * width}{C.RESET}")


def error(msg: str) -> None:
    """Display an error message in red."""
    print(f"  {C.RED}{C.BOLD} {msg}{C.RESET}")


def success(msg: str) -> None:
    """Display a success message in green."""
    print(f"  {C.GREEN}{C.BOLD} {msg}{C.RESET}")


def warning(msg: str) -> None:
    """Display a warning message in yellow."""
    print(f"  {C.YELLOW}{C.BOLD} {msg}{C.RESET}")


def info(msg: str) -> None:
    """Display an info message in gray."""
    print(f"  {C.GRAY}{msg}{C.RESET}")


def menu_item(number: int, text: str, color: str) -> None:
    """Print a numbered menu option."""
    print(f"  {color}{C.BOLD}{number:>3}.{C.RESET}  {text}")


def status_badge(text: str, is_good: bool) -> str:
    """Return colored badge text (e.g. Active/Inactive, Yes/No)."""
    if is_good:
        return f"{C.GREEN}{text}{C.RESET}"
    return f"{C.RED}{text}{C.RESET}"


def prompt(text: str) -> str:
    """Read a line of input with styled prompt. Returns stripped string."""
    return input(f"  {C.BRIGHT_WHITE}{text}{C.RESET}").strip()


def masked_input(prompt_text: str = "Password: ") -> str:
    """Read password with masked characters (platform-aware)."""
    print(f"  {C.BRIGHT_WHITE}{prompt_text}{C.RESET}", end="", flush=True)
    password = ""
    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                break
            if ch in ("\x08", "\b"):
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{C.YELLOW}*{C.RESET}")
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
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{C.YELLOW}*{C.RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


def clear_screen() -> None:
    """Clear the terminal (cls on Windows, clear on Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Wait for user to press Enter before continuing."""
    input(f"\n  {C.DIM}Press Enter to continue...{C.RESET}")
