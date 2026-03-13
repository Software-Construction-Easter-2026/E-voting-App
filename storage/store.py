import json
import os
import storage.state as state
from utils.logger import audit_logger

# Path to the JSON file where all system data is stored
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "evoting_data.json")


def save_data():
    # Ensure the data folder exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # Collect all application data into one structure
    payload = {
        "candidates": state.candidates,
        "candidate_id_counter": state.candidate_id_counter,
        "voting_stations": state.voting_stations,
        "station_id_counter": state.station_id_counter,
        "polls": state.polls,
        "poll_id_counter": state.poll_id_counter,
        "positions": state.positions,
        "position_id_counter": state.position_id_counter,
        "voters": state.voters,
        "voter_id_counter": state.voter_id_counter,
        "admins": state.admins,
        "admin_id_counter": state.admin_id_counter,
        "votes": state.votes,
        "audit_log": audit_logger.get_log(),
    }

    try:
        # Save the data to the JSON file
        with open(DATA_FILE, "w") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        raise RuntimeError(f"Save failed: {e}")


def load_data():
    # If the data file does not exist, skip loading
    if not os.path.exists(DATA_FILE):
        return

    try:
        # Read data from the JSON file
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        # Restore application state
        state.candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
        state.candidate_id_counter = data.get("candidate_id_counter", 1)

        state.voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
        state.station_id_counter = data.get("station_id_counter", 1)

        state.polls = {int(k): v for k, v in data.get("polls", {}).items()}
        state.poll_id_counter = data.get("poll_id_counter", 1)

        state.positions = {int(k): v for k, v in data.get("positions", {}).items()}
        state.position_id_counter = data.get("position_id_counter", 1)

        state.voters = {int(k): v for k, v in data.get("voters", {}).items()}
        state.voter_id_counter = data.get("voter_id_counter", 1)

        state.admins = {int(k): v for k, v in data.get("admins", {}).items()}
        state.admin_id_counter = data.get("admin_id_counter", 2)

        state.votes = data.get("votes", [])

        # Restore audit logs
        audit_logger.set_log(data.get("audit_log", []))

    except Exception as e:
        raise RuntimeError(f"Load failed: {e}")