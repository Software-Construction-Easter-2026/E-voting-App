
class DataStore:
    candidates = {}
    candidate_id_counter = 1
    voting_stations = {}
    station_id_counter = 1
    polls = {}
    poll_id_counter = 1
    positions = {}
    position_id_counter = 1
    voters = {}
    voter_id_counter = 1
    admins = {}
    admin_id_counter = 1
    votes = []
    audit_log = []
    current_user = None
    current_role = None

    MIN_CANDIDATE_AGE = 25
    MAX_CANDIDATE_AGE = 75
    REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]
    MIN_VOTER_AGE = 18