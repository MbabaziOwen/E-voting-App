import datetime
import json
import os
import hashlib


class DataStore:
    """Centralized data storage for the e-voting system."""
    
    def __init__(self):
        # Candidate data
        self.candidates = {}
        self.candidate_id_counter = 1
        
        # Voting station data
        self.voting_stations = {}
        self.station_id_counter = 1
        
        # Poll/Election data
        self.polls = {}
        self.poll_id_counter = 1
        
        # Position data
        self.positions = {}
        self.position_id_counter = 1
        
        # Voter data
        self.voters = {}
        self.voter_id_counter = 1
        
        # Admin data
        self.admins = {}
        self.admin_id_counter = 1
        
        # Voting records
        self.votes = []
        self.audit_log = []
        
        # Current session
        self.current_user = None
        self.current_role = None
        
        # Configuration constants
        self.MIN_CANDIDATE_AGE = 25
        self.MAX_CANDIDATE_AGE = 75
        self.REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]
        self.MIN_VOTER_AGE = 18
        
        self._initialize_default_admin()

    def _initialize_default_admin(self):
        """Create default admin account on first initialization."""
        self.admins[1] = {
            "id": 1,
            "username": "admin",
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "full_name": "System Administrator",
            "email": "admin@evote.com",
            "role": "super_admin",
            "created_at": str(datetime.datetime.now()),
            "is_active": True
        }
        self.admin_id_counter = 2

    def save_data(self):
        """Persist all data to JSON file."""
        data = {
            "candidates": self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": self.voting_stations,
            "station_id_counter": self.station_id_counter,
            "polls": self.polls,
            "poll_id_counter": self.poll_id_counter,
            "positions": self.positions,
            "position_id_counter": self.position_id_counter,
            "voters": self.voters,
            "voter_id_counter": self.voter_id_counter,
            "admins": self.admins,
            "admin_id_counter": self.admin_id_counter,
            "votes": self.votes,
            "audit_log": self.audit_log
        }
        try:
            with open("evoting_data.json", "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            raise Exception(f"Error saving data: {e}")

    def load_data(self):
        """Load all data from JSON file."""
        try:
            if os.path.exists("evoting_data.json"):
                with open("evoting_data.json", "r") as f:
                    data = json.load(f)
                
                self.candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
                self.candidate_id_counter = data.get("candidate_id_counter", 1)
                self.voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
                self.station_id_counter = data.get("station_id_counter", 1)
                self.polls = {int(k): v for k, v in data.get("polls", {}).items()}
                self.poll_id_counter = data.get("poll_id_counter", 1)
                self.positions = {int(k): v for k, v in data.get("positions", {}).items()}
                self.position_id_counter = data.get("position_id_counter", 1)
                self.voters = {int(k): v for k, v in data.get("voters", {}).items()}
                self.voter_id_counter = data.get("voter_id_counter", 1)
                self.admins = {int(k): v for k, v in data.get("admins", {}).items()}
                self.admin_id_counter = data.get("admin_id_counter", 1)
                self.votes = data.get("votes", [])
                self.audit_log = data.get("audit_log", [])
                return True
        except Exception as e:
            raise Exception(f"Error loading data: {e}")
