from datetime import datetime
from src.models.domain import Poll, Position, PollPosition

class PollService:
    MIN_CANDIDATE_AGE = 25

    def __init__(self, data_store):
        self.ds = data_store
        
    def create_position(self, current_user, title, description, level, max_winners, min_cand_age):
        if not title: return False, "Title cannot be empty."
        if level.lower() not in ["national", "regional", "local"]: return False, "Invalid level."
        
        try:
            max_winners = int(max_winners)
            if max_winners <= 0: return False, "Must be at least 1."
        except ValueError:
            return False, "Invalid number."
            
        min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else self.MIN_CANDIDATE_AGE
        
        pid = self.ds.position_id_counter
        pos = Position(
            id=pid, title=title, description=description, level=level.capitalize(),
            max_winners=max_winners, min_candidate_age=min_cand_age,
            is_active=True, created_at=str(datetime.now()), created_by=current_user.username
        )
        self.ds.positions[pid] = pos
        self.ds.position_id_counter += 1
        
        self.ds.log_action("CREATE_POSITION", current_user.username, f"Created position: {title} (ID: {pid})")
        self.ds.save_data()
        
        return True, f"Position '{title}' created! ID: {pid}"

    def update_position(self, current_user, pid, new_title, new_desc, new_level, new_seats):
        if pid not in self.ds.positions: return False, "Position not found."
        p = self.ds.positions[pid]
        
        if new_title: p.title = new_title
        if new_desc: p.description = new_desc
        if new_level and new_level.lower() in ["national", "regional", "local"]: p.level = new_level.capitalize()
        if new_seats:
            try: p.max_winners = int(new_seats)
            except ValueError: pass
            
        self.ds.log_action("UPDATE_POSITION", current_user.username, f"Updated position: {p.title}")
        self.ds.save_data()
        return True, "Position updated!"

    def delete_position(self, current_user, pid):
        if pid not in self.ds.positions: return False, "Position not found."
        
        for poll in self.ds.polls.values():
            for pp in poll.positions:
                if pp["position_id"] == pid and poll.status == "open": 
                    return False, f"Cannot delete - in active poll: {poll.title}"
                    
        self.ds.positions[pid].is_active = False
        self.ds.log_action("DELETE_POSITION", current_user.username, f"Deactivated position: {self.ds.positions[pid].title}")
        self.ds.save_data()
        return True, "Position deactivated."

    def create_poll(self, current_user, title, description, election_type, start_date, end_date, selected_position_ids, selected_station_ids):
        if not title: return False, "Title cannot be empty."
        
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd: return False, "End date must be after start date."
        except ValueError: return False, "Invalid date format."
        
        if not self.ds.positions: return False, "No positions available. Create positions first."
        if not selected_position_ids: return False, "No valid positions selected."
        if not self.ds.voting_stations: return False, "No voting stations. Create stations first."
        
        poll_positions = []
        for spid in selected_position_ids:
            if spid not in self.ds.positions or not self.ds.positions[spid].is_active: continue
            pos = self.ds.positions[spid]
            poll_positions.append({"position_id": spid, "position_title": pos.title, "candidate_ids": [], "max_winners": pos.max_winners})
            
        pid = self.ds.poll_id_counter
        poll = Poll(
            id=pid, title=title, description=description, election_type=election_type,
            start_date=start_date, end_date=end_date, positions=poll_positions,
            station_ids=selected_station_ids, status="draft", total_votes_cast=0,
            created_at=str(datetime.now()), created_by=current_user.username
        )
        self.ds.polls[pid] = poll
        self.ds.poll_id_counter += 1
        
        self.ds.log_action("CREATE_POLL", current_user.username, f"Created poll: {title} (ID: {pid})")
        self.ds.save_data()
        return True, f"Poll '{title}' created! ID: {pid}"

    def update_poll(self, current_user, pid, new_title, new_desc, new_type, new_start, new_end):
        if pid not in self.ds.polls: return False, "Poll not found."
        poll = self.ds.polls[pid]
        
        if poll.status == "open": return False, "Cannot update an open poll. Close it first."
        if poll.status == "closed" and poll.total_votes_cast > 0: return False, "Cannot update a poll with votes."
        
        if new_title: poll.title = new_title
        if new_desc: poll.description = new_desc
        if new_type: poll.election_type = new_type
        if new_start:
            try: datetime.strptime(new_start, "%Y-%m-%d"); poll.start_date = new_start
            except ValueError: pass
        if new_end:
            try: datetime.strptime(new_end, "%Y-%m-%d"); poll.end_date = new_end
            except ValueError: pass
            
        self.ds.log_action("UPDATE_POLL", current_user.username, f"Updated poll: {poll.title}")
        self.ds.save_data()
        return True, "Poll updated!"

    def delete_poll(self, current_user, pid):
        if pid not in self.ds.polls: return False, "Poll not found."
        poll = self.ds.polls[pid]
        
        if poll.status == "open": return False, "Cannot delete an open poll. Close it first."
        v_count = poll.total_votes_cast
        # We assume UI handles the warning for recorded votes
        
        deleted_title = poll.title
        del self.ds.polls[pid]
        self.ds.votes = [v for v in self.ds.votes if v.poll_id != pid]
        
        self.ds.log_action("DELETE_POLL", current_user.username, f"Deleted poll: {deleted_title}")
        self.ds.save_data()
        return True, f"Poll '{deleted_title}' deleted."

    def toggle_poll_status(self, current_user, pid, action):
        if pid not in self.ds.polls: return False, "Poll not found."
        poll = self.ds.polls[pid]
        
        if action == "open" and poll.status == "draft":
            if not any(pos.get("candidate_ids") for pos in poll.positions): 
                return False, "Cannot open - no candidates assigned."
            poll.status = "open"
            self.ds.log_action("OPEN_POLL", current_user.username, f"Opened poll: {poll.title}")
            self.ds.save_data()
            return True, f"Poll '{poll.title}' is now OPEN for voting!"
            
        elif action == "close" and poll.status == "open":
            poll.status = "closed"
            self.ds.log_action("CLOSE_POLL", current_user.username, f"Closed poll: {poll.title}")
            self.ds.save_data()
            return True, f"Poll '{poll.title}' is now CLOSED."
            
        elif action == "reopen" and poll.status == "closed":
            poll.status = "open"
            self.ds.log_action("REOPEN_POLL", current_user.username, f"Reopened poll: {poll.title}")
            self.ds.save_data()
            return True, "Poll reopened!"
            
        return False, "Invalid action for current poll status."

    def assign_candidates(self, current_user, pid, position_updates):
        if pid not in self.ds.polls: return False, "Poll not found."
        poll = self.ds.polls[pid]
        if poll.status == "open": return False, "Cannot modify candidates of an open poll."
        
        for pos_idx, new_cand_ids in position_updates.items():
            if 0 <= pos_idx < len(poll.positions):
                poll.positions[pos_idx]["candidate_ids"] = new_cand_ids
                
        self.ds.log_action("ASSIGN_CANDIDATES", current_user.username, f"Updated candidates for poll: {poll.title}")
        self.ds.save_data()
        return True, "Candidates assigned."
