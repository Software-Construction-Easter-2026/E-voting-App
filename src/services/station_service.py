from datetime import datetime
from src.models.domain import Station

class StationService:
    def __init__(self, data_store):
        self.ds = data_store
        
    def create_station(self, current_user, name, location, region, capacity, supervisor, contact, opening_time, closing_time):
        if not name: return False, "Name cannot be empty."
        if not location: return False, "Location cannot be empty."
        
        try:
            capacity = int(capacity)
            if capacity <= 0: return False, "Capacity must be positive."
        except ValueError:
            return False, "Invalid capacity."
            
        sid = self.ds.station_id_counter
        station = Station(
            id=sid, name=name, location=location, region=region, capacity=capacity,
            registered_voters=0, supervisor=supervisor, contact=contact,
            opening_time=opening_time, closing_time=closing_time, is_active=True,
            created_at=str(datetime.now()), created_by=current_user.username
        )
        self.ds.voting_stations[sid] = station
        self.ds.station_id_counter += 1
        
        self.ds.log_action("CREATE_STATION", current_user.username, f"Created station: {name} (ID: {sid})")
        self.ds.save_data()
        
        return True, f"Voting Station '{name}' created! ID: {sid}"

    def update_station(self, current_user, sid, new_name, new_location, new_region, new_capacity, new_supervisor, new_contact):
        if sid not in self.ds.voting_stations: return False, "Station not found."
        s = self.ds.voting_stations[sid]
        
        if new_name: s.name = new_name
        if new_location: s.location = new_location
        if new_region: s.region = new_region
        if new_capacity:
            try: s.capacity = int(new_capacity)
            except ValueError: pass
        if new_supervisor: s.supervisor = new_supervisor
        if new_contact: s.contact = new_contact
        
        self.ds.log_action("UPDATE_STATION", current_user.username, f"Updated station: {s.name} (ID: {sid})")
        self.ds.save_data()
        return True, f"Station '{s.name}' updated successfully!"

    def delete_station(self, current_user, sid):
        if sid not in self.ds.voting_stations: return False, "Station not found."
        
        # Check active voters
        voter_count = sum(1 for v in self.ds.voters.values() if v.station_id == sid)
        if voter_count > 0:
            return False, f"{voter_count} voters are registered at this station. Confirm deactivation explicitly required (implemented via UI flow)."
            
        name = self.ds.voting_stations[sid].name
        self.ds.voting_stations[sid].is_active = False
        self.ds.log_action("DELETE_STATION", current_user.username, f"Deactivated station: {name}")
        self.ds.save_data()
        return True, f"Station '{name}' deactivated."
        
    def get_voter_count(self, sid):
        return sum(1 for v in self.ds.voters.values() if v.station_id == sid)
