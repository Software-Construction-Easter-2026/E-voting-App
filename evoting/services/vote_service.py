import datetime
import hashlib


class VoteService:
    def __init__(self, repository, audit_service, voter_service, auth_service=None):
        self._repo = repository
        self._audit = audit_service
        self._voter_service = voter_service
        self._auth = auth_service

    def get_available_polls_for_voter(self, voter):
        station_id = voter["station_id"]
        has_voted_in = voter.get("has_voted_in", [])
        open_polls = {pid: p for pid, p in self._repo.polls.items() if p["status"] == "open"}
        return {
            pid: p for pid, p in open_polls.items()
            if pid not in has_voted_in and station_id in p.get("station_ids", [])
        }

    def get_open_polls(self):
        return {pid: p for pid, p in self._repo.polls.items() if p["status"] == "open"}

    def cast_vote(self, voter, poll_id, vote_choices, audit_user_label):
        if poll_id not in self._repo.polls:
            return False, "poll_not_found"
        poll = self._repo.polls[poll_id]
        if poll["status"] != "open":
            return False, "poll_not_open"
        if voter["station_id"] not in poll.get("station_ids", []):
            return False, "wrong_station"
        if poll_id in voter.get("has_voted_in", []):
            return False, "already_voted"
        vote_timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(f"{voter['id']}{poll_id}{vote_timestamp}".encode()).hexdigest()[:16]
        for choice in vote_choices:
            self._repo.votes.append({
                "vote_id": vote_hash + str(choice["position_id"]),
                "poll_id": poll_id,
                "position_id": choice["position_id"],
                "candidate_id": choice.get("candidate_id"),
                "voter_id": voter["id"],
                "station_id": voter["station_id"],
                "timestamp": vote_timestamp,
                "abstained": choice.get("abstained", False),
            })
        self._voter_service.record_voted_in(voter["id"], poll_id)
        if self._auth and self._auth.current_user and self._auth.current_user.get("id") == voter["id"]:
            if "has_voted_in" not in self._auth.current_user:
                self._auth.current_user["has_voted_in"] = []
            self._auth.current_user["has_voted_in"].append(poll_id)
        poll["total_votes_cast"] = poll.get("total_votes_cast", 0) + 1
        self._audit.log("CAST_VOTE", audit_user_label, f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
        return True, vote_hash
