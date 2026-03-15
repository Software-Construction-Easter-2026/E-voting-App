import sys
import os

# Add the project root directory to sys.path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.store import DataStore
from src.services.auth_service import AuthService
from src.services.voter_service import VoterService
from src.services.candidate_service import CandidateService
from src.services.station_service import StationService
from src.services.poll_service import PollService
from src.services.voting_service import VotingService
from src.services.audit_service import AuditService
from src.services.report_service import ReportService
from src.ui.main_menu import MainMenu

def main():
    # 1. Initialize Data Persistence
    ds = DataStore()
    
    # 2. Initialize Service Layer
    services = {
        'data_store': ds,
        'auth': AuthService(ds),
        'voter': VoterService(ds),
        'candidate': CandidateService(ds),
        'station': StationService(ds),
        'poll': PollService(ds),
        'voting': VotingService(ds),
        'audit': AuditService(ds),
        'report': ReportService(ds)
    }
    
    # 3. Initialize UI Layer
    app = MainMenu(services)
    
    # 4. Run loop
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n  Exiting system...")
        ds.save_data()

if __name__ == "__main__":
    main()
