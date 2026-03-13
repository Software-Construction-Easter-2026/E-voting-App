import datetime
import hashlib
import random
import string
import json
import os
import time
import sys
import DataStore


class SystemUtils:

    @staticmethod
    def initialize():
        if sys.platform == "win32":
            os.system("")


class Colors:

    ### base colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    ### foreground
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

    ## backgrounds
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_GRAY = "\033[100m"


class Themes:

    ### theme colors per context
    THEME_LOGIN = Colors.BRIGHT_CYAN
    THEME_ADMIN = Colors.BRIGHT_GREEN
    THEME_ADMIN_ACCENT = Colors.YELLOW
    THEME_VOTER = Colors.BRIGHT_BLUE
    THEME_VOTER_ACCENT = Colors.MAGENTA


class Formatter:

    @staticmethod
    def colored(text, color):
        return f"{color}{text}{Colors.RESET}"


class UI:

    @staticmethod
    def header(title, theme_color):
        width = 58
        top = f"  {theme_color}{'═' * width}{Colors.RESET}"
        mid = f"  {theme_color}{Colors.BOLD} {title.center(width - 2)} {Colors.RESET}{theme_color} {Colors.RESET}"
        bot = f"  {theme_color}{'═' * width}{Colors.RESET}"
        print(top)
        print(mid)
        print(bot)

    @staticmethod
    def subheader(title, theme_color):
        print(f"\n  {theme_color}{Colors.BOLD}▸ {title}{Colors.RESET}")

    @staticmethod
    def table_header(format_str, theme_color):
        print(f"  {theme_color}{Colors.BOLD}{format_str}{Colors.RESET}")

    @staticmethod
    def table_divider(width, theme_color):
        print(f"  {theme_color}{'─' * width}{Colors.RESET}")

    @staticmethod
    def error(msg):
        print(f"  {Colors.RED}{Colors.BOLD} {msg}{Colors.RESET}")

    @staticmethod
    def success(msg):
        print(f"  {Colors.GREEN}{Colors.BOLD} {msg}{Colors.RESET}")

    @staticmethod
    def warning(msg):
        print(f"  {Colors.YELLOW}{Colors.BOLD} {msg}{Colors.RESET}")

    @staticmethod
    def info(msg):
        print(f"  {Colors.GRAY}{msg}{Colors.RESET}")

    @staticmethod
    def menu_item(number, text, color):
        print(f"  {color}{Colors.BOLD}{number:>3}.{Colors.RESET}  {text}")

    @staticmethod
    def status_badge(text, is_good):
        if is_good:
            return f"{Colors.GREEN}{text}{Colors.RESET}"
        return f"{Colors.RED}{text}{Colors.RESET}"


class Input:
    @staticmethod
    def pause():
        input("Press Enter to continue...")

    @staticmethod
    def prompt(text):
        return input(f"  {Colors.BRIGHT_WHITE}{text}{Colors.RESET}").strip()

    @staticmethod
    def masked_input(prompt_text="Password: "):
        print(f"  {Colors.BRIGHT_WHITE}{prompt_text}{Colors.RESET}", end="", flush=True)
        password = ""
        if sys.platform == "win32":
            import msvcrt
            while True:
                ch = msvcrt.getwch()
                if ch == "\r" or ch == "\n":
                    print()
                    break
                elif ch == "\x08" or ch == "\b":
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{Colors.YELLOW}*{Colors.RESET}")
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
                    if ch == "\r" or ch == "\n":
                        print()
                        break
                    elif ch == "\x7f" or ch == "\x08":
                        if len(password) > 0:
                            password = password[:-1]
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    else:
                        password += ch
                        sys.stdout.write(f"{Colors.YELLOW}*{Colors.RESET}")
                        sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return password
    


class ScreenHelper:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def pause():
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.RESET}")


class IdGenerator:
    @staticmethod
    def generate_voter_card_number():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class PasswordHelper:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()


class AuditLogger:
    @staticmethod
    def log_action(action, user, details):
        DataStore.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details
        })


class PersistenceManager:
    @staticmethod
    def save_data():
        data = {
            "candidates": DataStore.candidates,
            "candidate_id_counter": DataStore.candidate_id_counter,
            "voting_stations": DataStore.voting_stations,
            "station_id_counter": DataStore.station_id_counter,
            "polls": DataStore.polls,
            "poll_id_counter": DataStore.poll_id_counter,
            "positions": DataStore.positions,
            "position_id_counter": DataStore.position_id_counter,
            "voters": DataStore.voters,
            "voter_id_counter": DataStore.voter_id_counter,
            "admins": DataStore.admins,
            "admin_id_counter": DataStore.admin_id_counter,
            "votes": DataStore.votes,
            "audit_log": DataStore.audit_log
        }
        try:
            with open("evoting_data.json", "w") as f:
                json.dump(data, f, indent=2)
            UI.info("Data saved successfully")
        except Exception as e:
            UI.error(f"Error saving data: {e}")

    @staticmethod
    def load_data():
        try:
            if os.path.exists("evoting_data.json"):
                with open("evoting_data.json", "r") as f:
                    data = json.load(f)

                # load all application state
                DataStore.candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
                DataStore.candidate_id_counter = data.get("candidate_id_counter", 1)
                DataStore.voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
                DataStore.station_id_counter = data.get("station_id_counter", 1)
                DataStore.polls = {int(k): v for k, v in data.get("polls", {}).items()}
                DataStore.poll_id_counter = data.get("poll_id_counter", 1)
                DataStore.positions = {int(k): v for k, v in data.get("positions", {}).items()}
                DataStore.position_id_counter = data.get("position_id_counter", 1)
                DataStore.voters = {int(k): v for k, v in data.get("voters", {}).items()}
                DataStore.voter_id_counter = data.get("voter_id_counter", 1)
                DataStore.admins = {int(k): v for k, v in data.get("admins", {}).items()}
                DataStore.admin_id_counter = data.get("admin_id_counter", 1)
                DataStore.votes = data.get("votes", [])
                DataStore.audit_log = data.get("audit_log", [])
                UI.info("Data loaded successfully")
        except Exception as e:
            UI.error(f"Error loading data: {e}")