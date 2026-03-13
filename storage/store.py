import json
import os
import storage.state as state

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'evoting_data.json')


def save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    payload = {
        "candidates":           state.candidates,
        "candidate_id_counter": state.candidate_id_counter,
        "voting_stations":      state.voting_stations,
        "station_id_counter":   state.station_id_counter,
        "polls":                state.polls,
        "poll_id_counter":      state.poll_id_counter,
        "positions":            state.positions,
        "position_id_counter":  state.position_id_counter,
        "voters":               state.voters,
        "voter_id_counter":     state.voter_id_counter,
        "admins":               state.admins,
        "admin_id_counter":     state.admin_id_counter,
        "votes":                state.votes,
        "audit_log":            state.audit_log,
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        raise RuntimeError(f"Save failed: {e}")


def load_data():
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        state.candidates            = {int(k): v for k, v in data.get("candidates", {}).items()}
        state.candidate_id_counter  = data.get("candidate_id_counter", 1)
        state.voting_stations       = {int(k): v for k, v in data.get("voting_stations", {}).items()}
        state.station_id_counter    = data.get("station_id_counter", 1)
        state.polls                 = {int(k): v for k, v in data.get("polls", {}).items()}
        state.poll_id_counter       = data.get("poll_id_counter", 1)
        state.positions             = {int(k): v for k, v in data.get("positions", {}).items()}
        state.position_id_counter   = data.get("position_id_counter", 1)
        state.voters                = {int(k): v for k, v in data.get("voters", {}).items()}
        state.voter_id_counter      = data.get("voter_id_counter", 1)
        state.admins                = {int(k): v for k, v in data.get("admins", {}).items()}
        state.admin_id_counter      = data.get("admin_id_counter", 2)
        state.votes                 = data.get("votes", [])
        state.audit_log             = data.get("audit_log", [])
    except Exception as e:
        raise RuntimeError(f"Load failed: {e}")
