# utils package – shared helpers, display, constants, and logging

from utils.colors import *

from utils.display import (
    colored, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge,
    prompt, clear_screen, pause,
)

from utils.helpers import (
    generate_voter_card_number,
    hash_password,
    calculate_age,
    current_timestamp,
    masked_input,
)

from utils.constants import (
    MIN_CANDIDATE_AGE,
    MAX_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
    MIN_VOTER_AGE,
    VALID_GENDERS,
    VALID_POSITION_LEVELS,
    VALID_ELECTION_TYPES,
    ADMIN_ROLES,
    DATA_FILE,
)

from utils.logger import audit_logger