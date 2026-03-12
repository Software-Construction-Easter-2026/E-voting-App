import hashlib
from datetime import datetime
from src.models.vote import Vote

class VotingService:
    def __init__(self, data_store):
        self.ds = data_store

    def cast_vote(self, current_user, pid, my_votes):
        if pid not in self.ds.polls: return False, "Invalid poll selection."
        poll = self.ds.polls[pid]
        
        vote_timestamp = str(datetime.now())
        vote_hash = hashlib.sha256(f"{current_user.id}{pid}{vote_timestamp}".encode()).hexdigest()[:16]
        
        for mv in my_votes:
            vote = Vote(
                vote_id=vote_hash + str(mv["position_id"]),
                poll_id=pid,
                position_id=mv["position_id"],
                candidate_id=mv["candidate_id"],
                voter_id=current_user.id,
                station_id=current_user.station_id,
                timestamp=vote_timestamp,
                abstained=mv["abstained"]
            )
            self.ds.votes.append(vote)
            
        current_user.has_voted_in.append(pid)
        for v in self.ds.voters.values():
            if v.id == current_user.id:
                v.has_voted_in.append(pid)
                break
                
        self.ds.polls[pid].total_votes_cast += 1
        
        self.ds.log_action("CAST_VOTE", current_user.voter_card_number, f"Voted in poll: {poll.title} (Hash: {vote_hash})")
        self.ds.save_data()
        
        return True, vote_hash
