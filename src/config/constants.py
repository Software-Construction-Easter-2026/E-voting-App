"""
Application-wide constants.
Keeps magic numbers and display theme in one place (Single Responsibility).
"""

# --- ANSI display (base) ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# --- Foreground colors ---
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

# --- Background colors ---
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"

# --- Theme colors per context (for consistent look) ---
THEME_LOGIN = BRIGHT_CYAN
THEME_ADMIN = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA

# --- Business rules: candidate eligibility ---
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]

# --- Business rules: voter eligibility ---
MIN_VOTER_AGE = 18

# --- Persistence ---
DATA_FILE = "evoting_data.json"
