import datetime
import hashlib
from services.auth_service import current_user


def _generate_vote_hash(user_id, poll_id, timestamp):
    return hashlib.sha256(f"{user_id}{poll_id}{timestamp}".encode()).hexdigest()[:16]


def get_open_polls(ctx):
    return {pid: p for pid, p in ctx.polls.get_all().items() if p.get("status") == "open"}


def get_open_polls_for_voter(ctx):
    user = current_user
    if not user:
        return {}

    open_polls = get_open_polls(ctx)
    station_id = user.get("station_id")
    voted = user.get("has_voted_in") or []

    return {
        pid: p
        for pid, p in open_polls.items()
        if pid not in voted and station_id in (p.get("station_ids") or [])
    }


def cast_vote(ctx, poll_id: int, position_choices: list):
    user = current_user

    if not user:
        return False, "Not logged in."

    poll = ctx.polls.get_by_id(poll_id)

    if not poll or poll.get("status") != "open":
        return False, "Invalid poll."

    if poll_id in (user.get("has_voted_in") or []):
        return False, "You have already voted in this poll."

    if user.get("station_id") not in (poll.get("station_ids") or []):
        return False, "Your station is not assigned to this poll."

    timestamp = str(datetime.datetime.now())
    vote_hash = _generate_vote_hash(user["id"], poll_id, timestamp)

    for mv in position_choices:
        ctx.votes.append({
            "vote_id": vote_hash + str(mv["position_id"]),
            "poll_id": poll_id,
            "position_id": mv["position_id"],
            "candidate_id": mv.get("candidate_id"),
            "voter_id": user["id"],
            "station_id": user["station_id"],
            "timestamp": timestamp,
            "abstained": mv.get("abstained", False),
        })

    for voter in ctx.voters.get_all().values():
        if voter.get("id") == user["id"]:
            voter.setdefault("has_voted_in", []).append(poll_id)
            break

    poll["total_votes_cast"] = (poll.get("total_votes_cast") or 0) + 1

    return True, vote_hash