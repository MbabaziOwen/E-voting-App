import json
import os
import hashlib
import datetime


class DataStore:
    """
    Central data container for the entire application.

    Replaces all global variables from the original monolith.
    Every service and UI class receives one shared instance of this
    class so all parts of the app read and write the same data.
    """

    def __init__(self):
        # ── Core data dictionaries 
        # Keys are integer IDs, values are plain dicts
        self.candidates      = {}
        self.voters          = {}
        self.admins          = {}
        self.polls           = {}
        self.positions       = {}
        self.voting_stations = {}

        # ── List storage 
        self.votes     = []   # each vote is a plain dict
        self.audit_log = []   # each entry is a plain dict

        # ── Auto-increment ID counters 
        self.candidate_id_counter = 1
        self.voter_id_counter     = 1
        self.admin_id_counter     = 2   # starts at 2 because admin id=1 is seeded
        self.poll_id_counter      = 1
        self.position_id_counter  = 1
        self.station_id_counter   = 1

        # ── Eligibility constants 
        self.MIN_CANDIDATE_AGE = 25
        self.MAX_CANDIDATE_AGE = 75
        self.MIN_VOTER_AGE     = 18
        self.REQUIRED_EDUCATION_LEVELS = [
            "Bachelor's Degree",
            "Master's Degree",
            "PhD",
            "Doctorate"
        ]

        # Seed the default admin account on first run
        self._seed_default_admin()

    # ── Private helpers 

    def _seed_default_admin(self):
        """
        Create the built-in super admin account.
        This ensures there is always at least one admin
        in the system even on a completely fresh start.

        Credentials:  username=admin  password=admin123
        """
        self.admins[1] = {
            "id":         1,
            "username":   "admin",
            "password":   hashlib.sha256("admin123".encode()).hexdigest(),
            "full_name":  "System Administrator",
            "email":      "admin@evote.com",
            "role":       "super_admin",
            "created_at": str(datetime.datetime.now()),
            "is_active":  True
        }

    # ── Persistence 

    def save(self):
        """
        Write the entire application state to data/evoting_data.json.
        Called after every action that modifies data.
        """
        # Make sure the data directory exists
        os.makedirs("data", exist_ok=True)

        data = {
            # Data collections
            "candidates":      self.candidates,
            "voters":          self.voters,
            "admins":          self.admins,
            "polls":           self.polls,
            "positions":       self.positions,
            "voting_stations": self.voting_stations,
            "votes":           self.votes,
            "audit_log":       self.audit_log,

            # ID counters — must be saved so IDs never repeat
            "candidate_id_counter": self.candidate_id_counter,
            "voter_id_counter":     self.voter_id_counter,
            "admin_id_counter":     self.admin_id_counter,
            "poll_id_counter":      self.poll_id_counter,
            "position_id_counter":  self.position_id_counter,
            "station_id_counter":   self.station_id_counter,
        }

        try:
            with open("data/evoting_data.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  Error saving data: {e}")

    def load(self):
        """
        Read data/evoting_data.json and restore all state.
        If the file does not exist (first run) this method does nothing
        and the app starts with empty collections.
        """
        path = "data/evoting_data.json"

        if not os.path.exists(path):
            return  # first run — nothing to load

        try:
            with open(path, "r") as f:
                data = json.load(f)

            # JSON keys are always strings — convert back to int for dict keys
            self.candidates = {
                int(k): v for k, v in data.get("candidates", {}).items()
            }
            self.voters = {
                int(k): v for k, v in data.get("voters", {}).items()
            }
            self.admins = {
                int(k): v for k, v in data.get("admins", {}).items()
            }
            self.polls = {
                int(k): v for k, v in data.get("polls", {}).items()
            }
            self.positions = {
                int(k): v for k, v in data.get("positions", {}).items()
            }
            self.voting_stations = {
                int(k): v for k, v in data.get("voting_stations", {}).items()
            }

            self.votes     = data.get("votes", [])
            self.audit_log = data.get("audit_log", [])

            # Restore counters so new IDs continue from where they left off
            self.candidate_id_counter = data.get("candidate_id_counter", 1)
            self.voter_id_counter     = data.get("voter_id_counter",     1)
            self.admin_id_counter     = data.get("admin_id_counter",     2)
            self.poll_id_counter      = data.get("poll_id_counter",      1)
            self.position_id_counter  = data.get("position_id_counter",  1)
            self.station_id_counter   = data.get("station_id_counter",   1)

        except Exception as e:
            print(f"  Error loading data: {e}")