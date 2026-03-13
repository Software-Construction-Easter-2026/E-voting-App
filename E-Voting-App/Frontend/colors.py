"""
colors.py

ANSI escape codes for terminal styling.
Matches the colour palette used in the original monolithic app.
"""

import sys
import os

# Enable ANSI on Windows
if sys.platform == "win32":
    os.system("")

# ── Base text styles ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
ITALIC = "\033[3m"

# ── Foreground colours ────────────────────────────────────────────────────────
BLACK        = "\033[30m"
RED          = "\033[31m"
GREEN        = "\033[32m"
YELLOW       = "\033[33m"
BLUE         = "\033[34m"
MAGENTA      = "\033[35m"
CYAN         = "\033[36m"
WHITE        = "\033[37m"
GRAY         = "\033[90m"
BRIGHT_RED   = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE  = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN  = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# ── Background colours ───────────────────────────────────────────────────────
BG_GREEN = "\033[42m"
BG_GRAY  = "\033[100m"

# ── Theme colours per context ─────────────────────────────────────────────────
THEME_LOGIN        = BRIGHT_CYAN
THEME_ADMIN        = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER        = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA