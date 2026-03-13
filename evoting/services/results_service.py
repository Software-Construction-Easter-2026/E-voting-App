class ResultsService:
    def __init__(self, repository):
        self._repo = repository

    def get_poll_results(self, poll_id):
        if poll_id not in self._repo.polls:
            return None
        poll = self._repo.polls[poll_id]
        result = {"poll": poll, "positions": []}
        for pos in poll["positions"]:
            vote_counts = {}
            abstain_count = 0
            for v in self._repo.votes:
                if v["poll_id"] == poll_id and v["position_id"] == pos["position_id"]:
                    if v.get("abstained"):
                        abstain_count += 1
                    else:
                        cid = v["candidate_id"]
                        vote_counts[cid] = vote_counts.get(cid, 0) + 1
            total = sum(vote_counts.values()) + abstain_count
            sorted_candidates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
            result["positions"].append({
                "position": pos,
                "vote_counts": vote_counts,
                "abstain_count": abstain_count,
                "total": total,
                "sorted_candidates": sorted_candidates,
            })
        return result

    def get_eligible_voters_count(self, poll_id):
        if poll_id not in self._repo.polls:
            return 0
        poll = self._repo.polls[poll_id]
        station_ids = set(poll.get("station_ids", []))
        return sum(
            1 for v in self._repo.voters.values()
            if v.get("is_verified") and v.get("is_active") and v.get("station_id") in station_ids
        )

    def get_detailed_statistics(self):
        candidates = self._repo.candidates
        voters = self._repo.voters
        stations = self._repo.voting_stations
        polls = self._repo.polls
        tc = len(candidates)
        ac = sum(1 for c in candidates.values() if c.get("is_active"))
        tv = len(voters)
        vv = sum(1 for v in voters.values() if v.get("is_verified"))
        av = sum(1 for v in voters.values() if v.get("is_active"))
        ts = len(stations)
        ast = sum(1 for s in stations.values() if s.get("is_active"))
        tp = len(polls)
        op = sum(1 for p in polls.values() if p["status"] == "open")
        cp = sum(1 for p in polls.values() if p["status"] == "closed")
        dp = sum(1 for p in polls.values() if p["status"] == "draft")
        overview = {
            "total_candidates": tc, "active_candidates": ac,
            "total_voters": tv, "verified_voters": vv, "active_voters": av,
            "total_stations": ts, "active_stations": ast,
            "total_polls": tp, "open_polls": op, "closed_polls": cp, "draft_polls": dp,
            "total_votes": len(self._repo.votes),
        }
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in voters.values():
            g = v.get("gender", "?")
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.get("age", 0)
            if age <= 25:
                age_groups["18-25"] += 1
            elif age <= 35:
                age_groups["26-35"] += 1
            elif age <= 45:
                age_groups["36-45"] += 1
            elif age <= 55:
                age_groups["46-55"] += 1
            elif age <= 65:
                age_groups["56-65"] += 1
            else:
                age_groups["65+"] += 1
        station_load = []
        for sid, s in stations.items():
            vc = sum(1 for v in voters.values() if v.get("station_id") == sid)
            cap = s.get("capacity", 1) or 1
            lp = (vc / cap * 100) if cap > 0 else 0
            station_load.append({"station": s, "voter_count": vc, "capacity": cap, "load_pct": lp})
        party_counts = {}
        for c in candidates.values():
            if c.get("is_active"):
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
        edu_counts = {}
        for c in candidates.values():
            if c.get("is_active"):
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
        return {
            "overview": overview,
            "gender_counts": gender_counts,
            "age_groups": age_groups,
            "station_load": station_load,
            "party_counts": party_counts,
            "edu_counts": edu_counts,
            "total_voters_for_pct": tv,
        }

    def get_station_wise_results(self, poll_id):
        if poll_id not in self._repo.polls:
            return None
        poll = self._repo.polls[poll_id]
        stations_data = []
        for sid in poll.get("station_ids", []):
            if sid not in self._repo.voting_stations:
                continue
            station = self._repo.voting_stations[sid]
            station_votes = [v for v in self._repo.votes if v["poll_id"] == poll_id and v["station_id"] == sid]
            unique_voters = len(set(v["voter_id"] for v in station_votes))
            registered = sum(
                1 for v in self._repo.voters.values()
                if v.get("station_id") == sid and v.get("is_verified") and v.get("is_active")
            )
            turnout_pct = (unique_voters / registered * 100) if registered > 0 else 0
            position_results = []
            for pos in poll["positions"]:
                pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v.get("abstained"):
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                total = sum(vc.values()) + ac
                position_results.append({
                    "position": pos,
                    "counts": vc,
                    "abstain_count": ac,
                    "total": total,
                })
            stations_data.append({
                "station": station,
                "unique_voters": unique_voters,
                "registered": registered,
                "turnout_pct": turnout_pct,
                "position_results": position_results,
            })
        return {"poll": poll, "stations_data": stations_data}
