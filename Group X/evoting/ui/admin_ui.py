# ui/admin_ui.py
from storage.data_store         import DataStore
from services.candidate_service import CandidateService
from services.station_service   import StationService
from services.poll_service      import PollService
from services.voter_service     import VoterService
from services.admin_service     import AdminService
from services.vote_service      import VoteService
from ui.display import (
    clear_screen, header, subheader, menu_item,
    prompt, error, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, DIM, RESET
)

class AdminUI:
    def __init__(self, store: DataStore):
        self.store     = store
        self.cand_svc  = CandidateService(store)
        self.stn_svc   = StationService(store)
        self.poll_svc  = PollService(store)
        self.voter_svc = VoterService(store)
        self.adm_svc   = AdminService(store)
        self.vote_svc  = VoteService(store)

    def dashboard(self, current_user):
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}  {DIM}│  Role: {current_user['role']}{RESET}")

            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1,  "Create Candidate",          THEME_ADMIN)
            menu_item(2,  "View All Candidates",        THEME_ADMIN)
            menu_item(3,  "Update Candidate",           THEME_ADMIN)
            menu_item(4,  "Delete Candidate",           THEME_ADMIN)
            menu_item(5,  "Search Candidates",          THEME_ADMIN)

            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6,  "Create Voting Station",      THEME_ADMIN)
            menu_item(7,  "View All Stations",          THEME_ADMIN)
            menu_item(8,  "Update Station",             THEME_ADMIN)
            menu_item(9,  "Delete Station",             THEME_ADMIN)

            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position",            THEME_ADMIN)
            menu_item(11, "View Positions",             THEME_ADMIN)
            menu_item(12, "Update Position",            THEME_ADMIN)
            menu_item(13, "Delete Position",            THEME_ADMIN)
            menu_item(14, "Create Poll",                THEME_ADMIN)
            menu_item(15, "View All Polls",             THEME_ADMIN)
            menu_item(16, "Update Poll",                THEME_ADMIN)
            menu_item(17, "Delete Poll",                THEME_ADMIN)
            menu_item(18, "Open/Close Poll",            THEME_ADMIN)
            menu_item(19, "Assign Candidates to Poll",  THEME_ADMIN)

            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters",            THEME_ADMIN)
            menu_item(21, "Verify Voter",               THEME_ADMIN)
            menu_item(22, "Deactivate Voter",           THEME_ADMIN)
            menu_item(23, "Search Voters",              THEME_ADMIN)

            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account",       THEME_ADMIN)
            menu_item(25, "View Admins",                THEME_ADMIN)
            menu_item(26, "Deactivate Admin",           THEME_ADMIN)

            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results",          THEME_ADMIN)
            menu_item(28, "View Detailed Statistics",   THEME_ADMIN)
            menu_item(29, "View Audit Log",             THEME_ADMIN)
            menu_item(30, "Station-wise Results",       THEME_ADMIN)

            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data",                  THEME_ADMIN)
            menu_item(32, "Logout",                     THEME_ADMIN)
            print()

            choice = prompt("Enter choice: ")

            if   choice == "1":  self.cand_svc.create(current_user)
            elif choice == "2":  self.cand_svc.view_all()
            elif choice == "3":  self.cand_svc.update(current_user)
            elif choice == "4":  self.cand_svc.delete(current_user)
            elif choice == "5":  self.cand_svc.search()
            elif choice == "6":  self.stn_svc.create(current_user)
            elif choice == "7":  self.stn_svc.view_all()
            elif choice == "8":  self.stn_svc.update(current_user)
            elif choice == "9":  self.stn_svc.delete(current_user)
            elif choice == "10": self.poll_svc.create_position(current_user)
            elif choice == "11": self.poll_svc.view_positions()
            elif choice == "12": self.poll_svc.update_position(current_user)
            elif choice == "13": self.poll_svc.delete_position(current_user)
            elif choice == "14": self.poll_svc.create(current_user)
            elif choice == "15": self.poll_svc.view_all()
            elif choice == "16": self.poll_svc.update(current_user)
            elif choice == "17": self.poll_svc.delete(current_user)
            elif choice == "18": self.poll_svc.open_close(current_user)
            elif choice == "19": self.poll_svc.assign_candidates(current_user)
            elif choice == "20": self.voter_svc.view_all()
            elif choice == "21": self.voter_svc.verify(current_user)
            elif choice == "22": self.voter_svc.deactivate(current_user)
            elif choice == "23": self.voter_svc.search()
            elif choice == "24": self.adm_svc.create(current_user)
            elif choice == "25": self.adm_svc.view_all()
            elif choice == "26": self.adm_svc.deactivate(current_user)
            elif choice == "27": self.vote_svc.view_results()
            elif choice == "28": self.vote_svc.view_statistics()
            elif choice == "29": self.adm_svc.view_audit_log()
            elif choice == "30": self.vote_svc.station_wise_results()
            elif choice == "31": self.store.save_data(); pause()
            elif choice == "32":
                from utils.helpers import log_action
                log_action(self.store, "LOGOUT",
                           current_user["username"], "Admin logged out")
                self.store.save_data()
                break
            else:
                error("Invalid choice.")
                pause()