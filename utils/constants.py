# All application-wide constants extracted from the original monolith.

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
MIN_VOTER_AGE = 18

REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]

VALID_GENDERS = ["M", "F", "OTHER"]

VALID_POSITION_LEVELS = ["national", "regional", "local"]

VALID_ELECTION_TYPES = ["General", "Primary", "By-election", "Referendum"]

# Maps menu-choice number → role name (used in admin creation)
ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

DATA_FILE = "evoting_data.json"
