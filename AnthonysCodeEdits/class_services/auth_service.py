import datetime
# TODO: from storage.data_store import DataStore  # Removed folder - import DataStore class for data persistence
# TODO: from ui.display import (  # Removed folder - import UI display functions for terminal output
#     prompt, masked_input, error, success, warning, info, 
#     clear_screen, pause, header, subheader, menu_item,
#     THEME_LOGIN, THEME_ADMIN, THEME_VOTER
# )
# TODO: from utils.helpers import hash_password, generate_voter_card_number, log_action  # Removed folder - import utility functions


class AuthService:
    """Handle authentication and user registration."""
    
    def __init__(self, store: DataStore):
        self.store = store
    
    def login(self, username=None, password=None):
        """Authenticate a user.

        If `username` and `password` are provided the method attempts to log in
        using those credentials and returns a tuple `(user_dict, role_str)` on
        success or `(None, None)` on failure.

        When called without arguments the old interactive menu is shown, allowing
        an admin or voter to log in or a new voter to register. The interactive
        path still returns the same tuple.
        """
        # parameterized login path
        if username is not None and password is not None:
            hashed = hash_password(password)
            # try admin first
            for aid, admin in self.store.admins.items():
                if admin["username"] == username and admin["password"] == hashed:
                    if not admin["is_active"]:
                        log_action(self.store, "LOGIN_FAILED", username, "Account deactivated")
                        return (None, None)
                    self.store.current_user = admin
                    self.store.current_role = "admin"
                    log_action(self.store, "LOGIN", username, "Admin login successful")
                    return (admin, "admin")
            # try voter
            for vid, voter in self.store.voters.items():
                if voter.get("voter_card_number") == username and voter["password"] == hashed:
                    if not voter["is_active"]:
                        log_action(self.store, "LOGIN_FAILED", username, "Voter account deactivated")
                        return (None, None)
                    if not voter.get("is_verified"):
                        log_action(self.store, "LOGIN_FAILED", username, "Voter not verified")
                        return (None, None)
                    self.store.current_user = voter
                    self.store.current_role = "voter"
                    log_action(self.store, "LOGIN", username, "Voter login successful")
                    return (voter, "voter")
            return (None, None)

        # interactive menu path (original behavior)
        clear_screen()
        header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin", THEME_LOGIN)
        menu_item(2, "Login as Voter", THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            return self._login_admin()
        elif choice == "2":
            return self._login_voter()
        elif choice == "3":
            self.register()
            return (None, None)
        elif choice == "4":
            print()
            info("Goodbye!")
            self.store.save_data()
            exit()
        else:
            error("Invalid choice.")
            pause()
            return (None, None)

    def _login_admin(self):
        """Attempt administrator login and return (user, role) or (None, None)."""
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()
        hashed = hash_password(password)
        
        for aid, admin in self.store.admins.items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    error("This account has been deactivated.")
                    log_action(self.store, "LOGIN_FAILED", username, "Account deactivated")
                    pause()
                    return (None, None)
                
                self.store.current_user = admin
                self.store.current_role = "admin"
                log_action(self.store, "LOGIN", username, "Admin login successful")
                print()
                success(f"Welcome, {admin['full_name']}!")
                pause()
                return (admin, "admin")
        
        error("Invalid credentials.")
        log_action(self.store, "LOGIN_FAILED", username, "Invalid admin credentials")
        pause()
        return (None, None)

    def _login_voter(self):
        """Attempt voter login and return (user, role) or (None, None)."""
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()
        hashed = hash_password(password)
        
        for vid, voter in self.store.voters.items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    error("This voter account has been deactivated.")
                    log_action(self.store, "LOGIN_FAILED", voter_card, "Voter account deactivated")
                    pause()
                    return (None, None)
                
                if not voter["is_verified"]:
                    warning("Your voter registration has not been verified yet.")
                    info("Please contact an admin to verify your registration.")
                    log_action(self.store, "LOGIN_FAILED", voter_card, "Voter not verified")
                    pause()
                    return (None, None)
                
                self.store.current_user = voter
                self.store.current_role = "voter"
                log_action(self.store, "LOGIN", voter_card, "Voter login successful")
                print()
                success(f"Welcome, {voter['full_name']}!")
                pause()
                return (voter, "voter")
        
        error("Invalid voter card number or password.")
        log_action(self.store, "LOGIN_FAILED", voter_card, "Invalid voter credentials")
        pause()
        return (None, None)

    def register(self, **kwargs):
        """Register a new voter.

        If keyword arguments are supplied they are used as field values. Supported
        keys match the interactive prompts (full_name, national_id, date_of_birth,
        gender, address, phone, email, password, station_choice).

        Returns the new voter dict or None if registration failed/cancelled.
        """
        # helper to prompt or fetch from kwargs
        def get_field(key, prompt_text, hide=False):
            if key in kwargs:
                return kwargs[key]
            return masked_input(prompt_text).strip() if hide else prompt(prompt_text)

        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()
        
        full_name = get_field("full_name", "Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return None
        
        national_id = get_field("national_id", "National ID Number: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return None
        
        # Check for duplicate national ID
        for vid, v in self.store.voters.items():
            if v["national_id"] == national_id:
                error("A voter with this National ID already exists.")
                pause()
                return None
        
        dob_str = get_field("date_of_birth", "Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < self.store.MIN_VOTER_AGE:
                error(f"You must be at least {self.store.MIN_VOTER_AGE} years old to register.")
                pause()
                return None
        except ValueError:
            error("Invalid date format.")
            pause()
            return None
        
        gender = get_field("gender", "Gender (M/F/Other): ").upper()
        if gender not in ["M", "F", "OTHER"]:
            error("Invalid gender selection.")
            pause()
            return None
        
        address = get_field("address", "Residential Address: ")
        phone = get_field("phone", "Phone Number: ")
        email = get_field("email", "Email Address: ")
        
        password = get_field("password", "Create Password: ", hide=True)
        if len(password) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return None
        
        confirm_password = get_field("confirm_password", "Confirm Password: ", hide=True)
        if password != confirm_password:
            error("Passwords do not match.")
            pause()
            return None
        
        if not self.store.voting_stations:
            error("No voting stations available. Contact admin.")
            pause()
            return None
        
        if "station_choice" in kwargs:
            station_choice = kwargs["station_choice"]
        else:
            # Select voting station interactively
            subheader("Available Voting Stations", "")
            for sid, station in self.store.voting_stations.items():
                if station["is_active"]:
                    from ui.display import BRIGHT_BLUE, RESET, DIM
                    print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
            try:
                station_choice = int(prompt("\nSelect your voting station ID: "))
            except ValueError:
                error("Invalid input.")
                pause()
                return None
            if station_choice not in self.store.voting_stations or not self.store.voting_stations[station_choice]["is_active"]:
                error("Invalid station selection.")
                pause()
                return None
        
        voter_card = generate_voter_card_number()
        vid = self.store.voter_id_counter
        
        self.store.voters[vid] = {
            "id": vid,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "address": address,
            "phone": phone,
            "email": email,
            "password": hash_password(password),
            "voter_card_number": voter_card,
            "station_id": station_choice,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter"
        }
        
        log_action(self.store, "REGISTER", full_name, f"New voter registered with card: {voter_card}")
        print()
        
        from ui.display import BRIGHT_YELLOW, BOLD
        success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")
        
        self.store.voter_id_counter += 1
        self.store.save_data()
        pause()
        return self.store.voters[vid]
