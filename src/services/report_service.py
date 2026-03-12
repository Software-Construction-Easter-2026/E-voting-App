class ReportService:
    def __init__(self, data_store):
        self.ds = data_store

    def get_system_overview(self):
        tc = len(self.ds.candidates)
        ac = sum(1 for c in self.ds.candidates.values() if c.is_active)
        tv = len(self.ds.voters)
        vv = sum(1 for v in self.ds.voters.values() if v.is_verified)
        av = sum(1 for v in self.ds.voters.values() if v.is_active)
        ts = len(self.ds.voting_stations)
        ast = sum(1 for s in self.ds.voting_stations.values() if s.is_active)
        tp = len(self.ds.polls)
        op = sum(1 for p in self.ds.polls.values() if p.status == "open")
        cp = sum(1 for p in self.ds.polls.values() if p.status == "closed")
        dp = sum(1 for p in self.ds.polls.values() if p.status == "draft")
        total_votes = len(self.ds.votes)
        
        return {
            "candidates": {"total": tc, "active": ac},
            "voters": {"total": tv, "verified": vv, "active": av},
            "stations": {"total": ts, "active": ast},
            "polls": {"total": tp, "open": op, "closed": cp, "draft": dp},
            "total_votes": total_votes
        }

    def get_voter_demographics(self):
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        
        for v in self.ds.voters.values():
            gender = v.gender if v.gender else "?"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            age = getattr(v, "age", 0)
            if age <= 25: age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else: age_groups["65+"] += 1
            
        return gender_counts, age_groups

    def get_station_loads(self):
        loads = []
        for sid, s in self.ds.voting_stations.items():
            vc = sum(1 for v in self.ds.voters.values() if v.station_id == sid)
            lp = (vc / s.capacity * 100) if getattr(s, "capacity", 0) > 0 else 0
            loads.append((s, vc, lp))
        return loads

    def get_candidate_distributions(self):
        party_counts = {}
        edu_counts = {}
        
        for c in self.ds.candidates.values():
            if c.is_active:
                party_counts[c.party] = party_counts.get(c.party, 0) + 1
                edu_counts[c.education] = edu_counts.get(c.education, 0) + 1
                
        # Sort parties by count descending
        sorted_parties = sorted(party_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_parties, edu_counts

    def get_tally_for_poll(self, pid):
        if pid not in self.ds.polls: return None
        
        poll = self.ds.polls[pid]
        total_eligible = sum(1 for v in self.ds.voters.values() 
                             if v.is_verified and v.is_active and v.station_id in poll.station_ids)
                             
        results = []
        for pos in poll.positions:
            vote_counts = {}
            abstain_count = 0
            total_pos_votes = 0
            
            # Count votes for this specific position in the poll
            for v in self.ds.votes:
                if v.poll_id == pid and v.position_id == pos["position_id"]:
                    total_pos_votes += 1
                    if v.abstained:
                        abstain_count += 1
                    else:
                        vote_counts[v.candidate_id] = vote_counts.get(v.candidate_id, 0) + 1
                        
            # Sort candidates by vote count
            sorted_candidates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
            candidate_details = []
            for cid, count in sorted_candidates:
                cand = self.ds.candidates.get(cid)
                candidate_details.append((cand, count))
                
            results.append({
                "position": pos,
                "total_votes": total_pos_votes,
                "winner_seats": pos["max_winners"],
                "candidates": candidate_details,
                "abstained": abstain_count
            })
            
        return {
            "poll": poll,
            "total_eligible": total_eligible,
            "turnout_pct": (poll.total_votes_cast / total_eligible * 100) if total_eligible > 0 else 0,
            "results": results
        }

    def get_station_wise_tally(self, pid):
        if pid not in self.ds.polls: return None
        poll = self.ds.polls[pid]
        
        station_results = []
        for sid in poll.station_ids:
            if sid not in self.ds.voting_stations: continue
            station = self.ds.voting_stations[sid]
            
            # Filter votes to this station and poll
            station_votes = [v for v in self.ds.votes if v.poll_id == pid and v.station_id == sid]
            
            # Find unique voters and registered active voters
            svc = len(set(v.voter_id for v in station_votes))
            ras = sum(1 for v in self.ds.voters.values() 
                      if v.station_id == sid and v.is_verified and v.is_active)
            
            turnout_pct = (svc / ras * 100) if ras > 0 else 0
            
            pos_results = []
            for pos in poll.positions:
                pv = [v for v in station_votes if v.position_id == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v.abstained: ac += 1
                    else: vc[v.candidate_id] = vc.get(v.candidate_id, 0) + 1
                    
                total = sum(vc.values()) + ac
                sorted_cands = sorted(vc.items(), key=lambda x: x[1], reverse=True)
                cand_details = [(self.ds.candidates.get(cid), count) for cid, count in sorted_cands]
                
                pos_results.append({
                    "position": pos,
                    "total_votes": total,
                    "candidates": cand_details,
                    "abstained": ac
                })
                
            station_results.append({
                "station": station,
                "registered": ras,
                "voted": svc,
                "turnout_pct": turnout_pct,
                "positions": pos_results
            })
            
        return {"poll": poll, "station_results": station_results}
