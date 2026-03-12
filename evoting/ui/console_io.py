import os
import sys

from evoting.core.colors import DIM, RESET, YELLOW


def init_console():
    if sys.platform == "win32":
        os.system("")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def prompt(text):
    from evoting.core.colors import BRIGHT_WHITE, RESET
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    from evoting.core.colors import BRIGHT_WHITE, RESET
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
        old = termios.tcgetattr(fd)
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
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return password
