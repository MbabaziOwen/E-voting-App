# services/voter_service.py
from storage.data_store import DataStore
from ui.display import (
    clear_screen, header, subheader, menu_item, prompt,
    error, success, warning, info, pause,
    table_header, table_divider, status_badge,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, DIM, RESET
)
from utils.helpers import log_action


class VoterService:
    def __init__(self, store: DataStore):
        self.store = store

    def view_all(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        if not self.store.voters:
            print()
            info("No voters registered.")
            pause()
            return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN
        )
        table_divider(70, THEME_ADMIN)
        for vid, v in self.store.voters.items():
            verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
            active   = status_badge("Yes", True) if v["is_active"]   else status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
        verified_count   = sum(1 for v in self.store.voters.values() if v["is_verified"])
        unverified_count = sum(1 for v in self.store.voters.values() if not v["is_verified"])
        print(f"\n  {DIM}Total: {len(self.store.voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        pause()

    def verify(self, current_user):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        unverified = {vid: v for vid, v in self.store.voters.items() if not v["is_verified"]}
        if not unverified:
            print()
            info("No unverified voters.")
            pause()
            return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for vid, v in unverified.items():
            print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
        print()
        menu_item(1, "Verify a single voter",    THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input.")
                pause()
                return
            if vid not in self.store.voters:
                error("Voter not found.")
                pause()
                return
            if self.store.voters[vid]["is_verified"]:
                info("Already verified.")
                pause()
                return
            self.store.voters[vid]["is_verified"] = True
            log_action(self.store, "VERIFY_VOTER",
                       current_user["username"],
                       f"Verified voter: {self.store.voters[vid]['full_name']}")
            print()
            success(f"Voter '{self.store.voters[vid]['full_name']}' verified!")
            self.store.save_data()
        elif choice == "2":
            count = 0
            for vid in unverified:
                self.store.voters[vid]["is_verified"] = True
                count += 1
            log_action(self.store, "VERIFY_ALL_VOTERS",
                       current_user["username"], f"Verified {count} voters")
            print()
            success(f"{count} voters verified!")
            self.store.save_data()
        pause()

    def deactivate(self, current_user):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self.store.voters:
            print()
            info("No voters found.")
            pause()
            return
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if vid not in self.store.voters:
            error("Voter not found.")
            pause()
            return
        if not self.store.voters[vid]["is_active"]:
            info("Already deactivated.")
            pause()
            return
        if prompt(f"Deactivate '{self.store.voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
            self.store.voters[vid]["is_active"] = False
            log_action(self.store, "DEACTIVATE_VOTER",
                       current_user["username"],
                       f"Deactivated voter: {self.store.voters[vid]['full_name']}")
            print()
            success("Voter deactivated.")
            self.store.save_data()
        pause()

    def search(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name",              THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID",       THEME_ADMIN)
        menu_item(4, "Station",           THEME_ADMIN)
        choice = prompt("\nChoice: ")
        results = []
        if choice == "1":
            term = prompt("Name: ").lower()
            results = [v for v in self.store.voters.values() if term in v["full_name"].lower()]
        elif choice == "2":
            term = prompt("Card Number: ")
            results = [v for v in self.store.voters.values() if term == v["voter_card_number"]]
        elif choice == "3":
            term = prompt("National ID: ")
            results = [v for v in self.store.voters.values() if term == v["national_id"]]
        elif choice == "4":
            try:
                sid = int(prompt("Station ID: "))
                results = [v for v in self.store.voters.values() if v["station_id"] == sid]
            except ValueError:
                error("Invalid input.")
                pause()
                return
        else:
            error("Invalid choice.")
            pause()
            return
        if not results:
            print()
            info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
        pause()