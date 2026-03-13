# In-memory application state for the e-voting system

# ── Counters ─────────────────────────────────────────
candidate_id_counter = 1
voter_id_counter = 1
station_id_counter = 1
poll_id_counter = 1
position_id_counter = 1
admin_id_counter = 2


# ── Data Stores ──────────────────────────────────────
candidates = {}
voters = {}
voting_stations = {}
polls = {}
positions = {}
admins = {}
votes = []


# ── Session Information ──────────────────────────────
current_user = None
current_role = None