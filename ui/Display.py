#Reusable terminal display helpers and theme constants for the e-voting system.

import os
import sys


if sys.platform == "win32":
    os.system("")


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"


BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"


BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"


THEME_LOGIN = BRIGHT_CYAN
THEME_ADMIN = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


def colored(text, color):
    #Return text wrapped in the given color.
    return f"{color}{text}{RESET}"


def header(title, theme_color):
    #Display a boxed screen header.
    width = 58
    top_border = f"  {theme_color}{'═' * width}{RESET}"
    middle_line = (
        f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}"
        f"{theme_color} {RESET}"
    )
    bottom_border = f"  {theme_color}{'═' * width}{RESET}"

    print(top_border)
    print(middle_line)
    print(bottom_border)


def subheader(title, theme_color):
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    print(f"  {theme_color}{'─' * width}{RESET}")


def display_error(msg):
    print(f"  {RED}{BOLD} {msg}{RESET}")


def display_success(msg):
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def display_warning(msg):
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def display_info_message(msg):
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number, text, color):
    #Display a numbered menu item.
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    if is_good:
        return f"{GREEN}{text}{RESET}"
    return f"{RED}{text}{RESET}"


def prompt(text):
    #Display a styled input prompt and return stripped input.
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    #Display a password prompt and mask typed characters.
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt

        while True:
            char = msvcrt.getwch()

            if char in ("\r", "\n"):
                print()
                break

            if char in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            if char == "\x03":
                raise KeyboardInterrupt

            password += char
            sys.stdout.write(f"{YELLOW}*{RESET}")
            sys.stdout.flush()

    else:
        import termios
        import tty

        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)

        try:
            tty.setraw(file_descriptor)

            while True:
                char = sys.stdin.read(1)

                if char in ("\r", "\n"):
                    print()
                    break

                if char in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue

                if char == "\x03":
                    raise KeyboardInterrupt

                password += char
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()

        finally:
            termios.tcsetattr(
                file_descriptor,
                termios.TCSADRAIN,
                old_settings,
            )

    return password