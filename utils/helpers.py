# Pure utility functions with no side-effects.
# Any module in the project may import from here freely.

import datetime
import hashlib
import random
import string
import sys


def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of a plain-text password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number() -> str:
    """Generate a random 12-character alphanumeric voter card number."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def calculate_age(dob_str: str) -> int:
    """
    Parse a 'YYYY-MM-DD' date string and return the person's age in whole years.
    Raises ValueError if the format is incorrect.
    """
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    return (datetime.datetime.now() - dob).days // 365


def current_timestamp() -> str:
    """Return the current date-time as a readable string."""
    return str(datetime.datetime.now())


def masked_input(prompt_text: str = "Password: ") -> str:
    """
    Read password input and show '*' instead of the real characters.
    Works on both Windows and Linux/macOS terminals.
    """
    print(prompt_text, end="", flush=True)
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
            else:
                password += ch
                sys.stdout.write("*")
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
                else:
                    password += ch
                    sys.stdout.write("*")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password