import hashlib
import datetime

# ── Counters ──────────────────────────────────────────────────────────────────
candidate_id_counter  = 1
voter_id_counter      = 1
station_id_counter    = 1
poll_id_counter       = 1
position_id_counter   = 1
admin_id_counter      = 2

# ── Data Stores ───────────────────────────────────────────────────────────────
candidates      = {}
voters          = {}
voting_stations = {}
polls           = {}
positions       = {}
admins          = {}
votes           = []
audit_log       = []

# ── Session ───────────────────────────────────────────────────────────────────
current_user = None
current_role = None

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_VOTER_AGE     = 18
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate"
]

# ── Seed Default Super Admin ──────────────────────────────────────────────────
admins[1] = {
    "id":         1,
    "username":   "admin",
    "password":   hashlib.sha256("admin123".encode()).hexdigest(),
    "full_name":  "System Administrator",
    "email":      "admin@evote.com",
    "role":       "super_admin",
    "created_at": str(datetime.datetime.now()),
    "is_active":  True
}
