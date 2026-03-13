from typing import Dict, Any


class VoterService:

    def view_all(self):
        # Exact logic from view_all_voters()
        from ..e_voting_console_app import (
            clear_screen, header, table_header, table_divider, status_badge,
            THEME_ADMIN, BOLD, DIM, RESET, pause, info
        )
        
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        
        if not self.store.voters:
            print()
            info("No voters registered.")
            pause()
            return
        
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        
        for vid, v in self.store.voters.items():
            verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
            active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<10} {active}")
        
        verified_count = sum(1 for v in self.store.voters.values() if v["is_verified"])
        unverified_count = sum(1 for v in self.store.voters.values() if not v["is_verified"])
        print(f"\n  Total: {len(self.store.voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}")
        pause()

    def verify(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from verify_voter()
        from ..e_voting_console_app import (
            clear_screen, header, subheader, prompt, info, error, success, pause, 
            THEME_ADMIN, THEME_ADMIN_ACCENT, status_badge, RESET
        )
        
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        
        unverified = {vid: v for vid, v in self.store.voters.items() if not v["is_verified"]}
        if not unverified:
            print()
            info("No unverified voters.")
            pause()
            return False
        
        print("Unverified Voters:")
        for vid, v in unverified.items():
            print(f"  {THEME_ADMIN}{v['id']}. {v['full_name']} │ NID: {v['national_id']} │ Card: {v['voter_card_number']}")
        
        print()
        print("1. Verify a single voter")
        print("2. Verify all pending voters")
        choice = prompt("\nChoice: ")
        
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input.")
                pause()
                return False
            
            if vid not in self.store.voters:
                error("Voter not found.")
                pause()
                return False
            
            if self.store.voters[vid]["is_verified"]:
                info("Already verified.")
                pause()
                return False
            
            self.store.voters[vid]["is_verified"] = True
            self.store.log_action("VERIFY_VOTER", current_user["username"], 
                                f"Verified voter: {self.store.voters[vid]['full_name']}")
            print()
            success(f"Voter '{self.store.voters[vid]['full_name']}' verified!")
            self.store.save()
            
        elif choice == "2":
            count = 0
            for vid in list(unverified.keys()):
                self.store.voters[vid]["is_verified"] = True
                count += 1
            self.store.log_action("VERIFY_ALL_VOTERS", current_user["username"], f"Verified {count} voters")
            print()
            success(f"{count} voters verified!")
            self.store.save()
        
        pause()
        return True

    def deactivate(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from deactivate_voter()
        from ..e_voting_console_app import (
            clear_screen, header, prompt, error, info, success, pause, THEME_ADMIN, RESET
        )
        
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        
        if not self.store.voters:
            print()
            info("No voters found.")
            pause()
            return False
        
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if vid not in self.store.voters:
            error("Voter not found.")
            pause()
            return False
        
        if not self.store.voters[vid]["is_active"]:
            info("Already deactivated.")
            pause()
            return False
        
        if prompt(f"Deactivate '{self.store.voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
            self.store.voters[vid]["is_active"] = False
            self.store.log_action("DEACTIVATE_VOTER", current_user["username"], 
                                f"Deactivated voter: {self.store.voters[vid]['full_name']}")
            print()
            success("Voter deactivated.")
            self.store.save()
        pause()
        return True

    def search(self):
        # Exact logic from search_voters()
        from ..e_voting_console_app import (
            clear_screen, header, subheader, menu_item, prompt, info, error, pause,
            THEME_ADMIN, THEME_ADMIN_ACCENT, status_badge, BOLD, DIM, RESET
        )
        
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        
        print("Search by:")
        print("1. Name")
        print("2. Voter Card Number")
        print("3. National ID")
        print("4. Station")
        
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
            print(f"\n{BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
                print(f"  ID: {v['id']} │ {v['full_name']} │ Card: {v['voter_card_number']} │ {verified}")
        pause()

