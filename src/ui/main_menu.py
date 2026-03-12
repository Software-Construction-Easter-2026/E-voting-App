import sys
from src.ui.theme import *
from src.ui.admin_views import AdminViews
from src.ui.voter_views import VoterViews

class MainMenu:
    def __init__(self, services):
        self.auth_service = services['auth']
        self.voter_service = services['voter']
        self.ds = services['data_store']
        
        self.admin_views = AdminViews(services)
        self.voter_views = VoterViews(services)

    def run(self):
        print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
        self.ds.load_data()
        
        import time
        time.sleep(1)
        
        while True:
            clear_screen()
            current_user, role = self.login_flow()
            if current_user:
                if role == "admin":
                    self.admin_views.dashboard(current_user)
                elif role == "voter":
                    self.voter_views.dashboard(current_user)

    def login_flow(self):
        header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin", THEME_LOGIN)
        menu_item(2, "Login as Voter", THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            clear_screen()
            header("ADMIN LOGIN", THEME_ADMIN)
            print()
            username = prompt("Username: ")
            password = masked_input("Password: ").strip()
            
            success_flag, msg, user = self.auth_service.login_admin(username, password)
            if success_flag:
                print()
                success(msg)
                pause()
                return user, "admin"
            else:
                error(msg)
                pause()
                return None, None

        elif choice == "2":
            clear_screen()
            header("VOTER LOGIN", THEME_VOTER)
            print()
            voter_card = prompt("Voter Card Number: ")
            password = masked_input("Password: ").strip()
            
            success_flag, msg, user = self.auth_service.login_voter(voter_card, password)
            if success_flag:
                print()
                success(msg)
                pause()
                return user, "voter"
            else:
                if "verified" in msg.lower():
                    warning(msg.split('\n')[0])
                    info(msg.split('\n')[1])
                else:
                    error(msg)
                pause()
                return None, None

        elif choice == "3":
            self.register_voter_view()
            return None, None
            
        elif choice == "4":
            print()
            info("Goodbye!")
            self.ds.save_data()
            sys.exit()
            
        else:
            error("Invalid choice.")
            pause()
            return None, None

    def register_voter_view(self):
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()
        
        full_name = prompt("Full Name: ")
        if not full_name: error("Name cannot be empty."); pause(); return
        
        national_id = prompt("National ID Number: ")
        if not national_id: error("National ID cannot be empty."); pause(); return
        
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        
        gender = prompt("Gender (M/F/Other): ").upper()
        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")
        
        password = masked_input("Create Password: ").strip()
        confirm_password = masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            error("Passwords do not match.")
            pause()
            return
            
        stations = self.voter_service.get_all_active_stations()
        if not stations:
            error("No voting stations available. Contact admin.")
            pause()
            return
            
        subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in stations.items():
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station.name} {DIM}- {station.location}{RESET}")
            
        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
            
        success_flag, result = self.voter_service.register_voter(
            full_name, national_id, dob_str, gender, address, phone, email, password, station_choice
        )
        
        if success_flag:
            print()
            success("Registration successful!")
            print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{result}{RESET}")
            warning("IMPORTANT: Save this number! You need it to login.")
            info("Your registration is pending admin verification.")
        else:
            error(result)
            
        pause()
