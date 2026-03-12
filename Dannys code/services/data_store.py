import json
import os
import datetime
from typing import Dict, Any, List

class DataStore:
    def __init__(self, data_file: str = 'Dannys code/evoting_data.json'):
        self.data_file = data_file
        self.candidates: Dict[int, Dict[str, Any]] = {}
        self.candidate_id_counter = 1
        self.voting_stations: Dict[int, Dict[str, Any]] = {}
        self.station_id_counter = 1
        self.polls: Dict[int, Dict[str, Any]] = {}
        self.poll_id_counter = 1
        self.positions: Dict[int, Dict[str, Any]] = {}
        self.position_id_counter = 1
        self.voters: Dict[int, Dict[str, Any]] = {}
        self.voter_id_counter = 1
        self.admins: Dict[int, Dict[str, Any]] = {}
        self.admin_id_counter = 1
        self.votes: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.load()

    def save(self):
        data = {
            'candidates': self.candidates, 'candidate_id_counter': self.candidate_id_counter,
            'voting_stations': self.voting_stations, 'station_id_counter': self.station_id_counter,
            'polls': self.polls, 'poll_id_counter': self.poll_id_counter,
            'positions': self.positions, 'position_id_counter': self.position_id_counter,
            'voters': self.voters, 'voter_id_counter': self.voter_id_counter,
            'admins': self.admins, 'admin_id_counter': self.admin_id_counter,
            'votes': self.votes, 'audit_log': self.audit_log
        }
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def load(self):
        if not os.path.exists(self.data_file):
            self._init_default_admin()
            self.save()
            return
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            self.candidates = {int(k): v for k, v in data.get('candidates', {}).items()}
            self.candidate_id_counter = data.get('candidate_id_counter', 1)
            self.voting_stations = {int(k): v for k, v in data.get('voting_stations', {}).items()}
            self.station_id_counter = data.get('station_id_counter', 1)
            self.polls = {int(k): v for k, v in data.get('polls', {}).items()}
            self.poll_id_counter = data.get('poll_id_counter', 1)
            self.positions = {int(k): v for k, v in data.get('positions', {}).items()}
            self.position_id_counter = data.get('position_id_counter', 1)
            self.voters = {int(k): v for k, v in data.get('voters', {}).items()}
            self.voter_id_counter = data.get('voter_id_counter', 1)
            self.admins = {int(k): v for k, v in data.get('admins', {}).items()}
            self.admin_id_counter = data.get('admin_id_counter', 1)
            self.votes = data.get('votes', [])
            self.audit_log = data.get('audit_log', [])
        except Exception as e:
            print(f"Load error: {e}")

    def _init_default_admin(self):
        import hashlib
        self.admins[1] = {
            "id": 1, "username": "admin",
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "full_name": "System Administrator", "email": "admin@evote.com",
            "role": "super_admin", "created_at": str(datetime.datetime.now()), "is_active": True
        }
        self.admin_id_counter = 2

    def log_action(self, action: str, user: str, details: str):
        self.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action, "user": user, "details": details
        })

