# ui/voter_ui.py
from storage.data_store    import DataStore
from services.vote_service import VoteService
from ui.display import (
    clear_screen, header, subheader, menu_item,
    prompt, error, pause, success, info, warning,
    masked_input, status_badge, table_header, table_divider,
    THEME_VOTER, THEME_VOTER_ACCENT, THEME_ADMIN,
    BOLD, DIM, RESET, BRIGHT_YELLOW, GRAY, GREEN,
    BRIGHT_GREEN, BRIGHT_CYAN, BG_GREEN, BLACK, ITALIC
)
from utils.helpers import hash_password, log_action


class VoterUI:
    def __init__(self, store: DataStore):
        self.store    = store
        self.vote_svc = VoteService(store)

    def dashboard(self, current_user):
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            station_name = self.store.voting_stations.get(
                current_user["station_id"], {}
            ).get("name", "Unknown")
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}")
            print(f"  {DIM}    Card: {current_user['voter_card_number']}  │  Station: {station_name}{RESET}")
            print()
            menu_item(1, "View Open Polls",              THEME_VOTER)
            menu_item(2, "Cast Vote",                    THEME_VOTER)
            menu_item(3, "View My Voting History",       THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)",  THEME_VOTER)
            menu_item(5, "View My Profile",              THEME_VOTER)
            menu_item(6, "Change Password",              THEME_VOTER)
            menu_item(7, "Logout",                       THEME_VOTER)
            print()

            choice = prompt("Enter choice: ")

            if   choice == "1": self.vote_svc.view_open_polls(current_user)
            elif choice == "2": self.vote_svc.cast_vote(current_user)
            elif choice == "3": self.vote_svc.view_voting_history(current_user)
            elif choice == "4": self.vote_svc.view_closed_results(current_user)
            elif choice == "5": self._view_profile(current_user)
            elif choice == "6": self._change_password(current_user)
            elif choice == "7":
                log_action(self.store.audit_log, "LOGOUT",
                           current_user["voter_card_number"], "Voter logged out")
                self.store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    def _view_profile(self, current_user):
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        v = current_user
        station_name = self.store.voting_stations.get(
            v["station_id"], {}
        ).get("name", "Unknown")
        print()
        for label, value in [
            ("Name",        v['full_name']),
            ("National ID", v['national_id']),
            ("Voter Card",  f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
            ("Date of Birth", v['date_of_birth']),
            ("Age",         v['age']),
            ("Gender",      v['gender']),
            ("Address",     v['address']),
            ("Phone",       v['phone']),
            ("Email",       v['email']),
            ("Station",     station_name),
            ("Verified",    status_badge('Yes', True) if v['is_verified']
                            else status_badge('No', False)),
            ("Registered",  v['registered_at']),
            ("Polls Voted", len(v.get('has_voted_in', [])))
        ]:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        pause()

    def _change_password(self, current_user):
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        print()
        old_pass = masked_input("Current Password: ").strip()
        if hash_password(old_pass) != current_user["password"]:
            error("Incorrect current password.")
            pause()
            return
        new_pass = masked_input("New Password: ").strip()
        if len(new_pass) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return
        confirm_pass = masked_input("Confirm New Password: ").strip()
        if new_pass != confirm_pass:
            error("Passwords do not match.")
            pause()
            return
        current_user["password"] = hash_password(new_pass)
        for vid, v in self.store.voters.items():
            if v["id"] == current_user["id"]:
                v["password"] = hash_password(new_pass)
                break
        log_action(self.store.audit_log, "CHANGE_PASSWORD",
                current_user["voter_card_number"], "Password changed")
        print()
        success("Password changed successfully!")
        self.store.save()
        pause()