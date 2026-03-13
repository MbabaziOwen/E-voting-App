import datetime
# TODO: from storage.data_store import DataStore  # Removed folder - import DataStore class for data persistence
# TODO: from ui.display import (  # Removed folder - import UI display functions for terminal output
#     prompt, error, success, warning, info, clear_screen, pause,
#     header, subheader, menu_item, table_header, table_divider, status_badge,
#     THEME_ADMIN, THEME_ADMIN_ACCENT, RESET, BOLD, DIM
# )
# TODO: from utils.helpers import log_action  # Removed folder - import log_action utility function


class CandidateService:
    """Handle candidate management operations."""
    
    def __init__(self, store: DataStore):
        self.store = store
    
    def create(self, current_user):
        """Create a new candidate.

        Returns the created candidate dict, or None if the operation was cancelled or failed.
        """
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return None
        
        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return None
        
        # Check for duplicate national ID
        for cid, c in self.store.candidates.items():
            if c["national_id"] == national_id:
                error("A candidate with this National ID already exists.")
                pause()
                return None
        
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            error("Invalid date format.")
            pause()
            return None
        
        if age < self.store.MIN_CANDIDATE_AGE:
            error(f"Candidate must be at least {self.store.MIN_CANDIDATE_AGE} years old. Current age: {age}")
            pause()
            return None
        if age > self.store.MAX_CANDIDATE_AGE:
            error(f"Candidate must not be older than {self.store.MAX_CANDIDATE_AGE}. Current age: {age}")
            pause()
            return None
        
        gender = prompt("Gender (M/F/Other): ").upper()
        
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(self.store.REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        
        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(self.store.REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice.")
                pause()
                return None
            education = self.store.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input.")
            pause()
            return None
        
        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            error("Candidates with criminal records are not eligible.")
            log_action(self.store, "CANDIDATE_REJECTED", current_user["username"],
                      f"Candidate {full_name} rejected - criminal record")
            pause()
            return None
        
        years_experience = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_experience)
        except ValueError:
            years_experience = 0
        
        cid = self.store.candidate_id_counter
        self.store.candidates[cid] = {
            "id": cid,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "education": education,
            "party": party,
            "manifesto": manifesto,
            "address": address,
            "phone": phone,
            "email": email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": current_user["username"]
        }
        
        log_action(self.store, "CREATE_CANDIDATE", current_user["username"],
                  f"Created candidate: {full_name} (ID: {cid})")
        print()
        success(f"Candidate '{full_name}' created successfully! ID: {cid}")
        self.store.candidate_id_counter += 1
        self.store.save_data()
        pause()
        return self.store.candidates[cid]
    
    def view_all(self):
        """Display all candidates and return them as a list."""
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        
        candidates = list(self.store.candidates.values())
        if not candidates:
            print()
            info("No candidates found.")
            pause()
            return []
        
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        table_divider(85, THEME_ADMIN)
        
        for c in candidates:
            status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
        
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()
        return candidates
    
    def update(self, current_user) -> bool:
        """Update candidate information.

        Returns True if the candidate was successfully updated, False otherwise.
        """
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return False
        
        print()
        for cid, c in self.store.candidates.items():
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
        
        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if cid not in self.store.candidates:
            error("Candidate not found.")
            pause()
            return False
        
        c = self.store.candidates[cid]
        print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
        info("Press Enter to keep current value\n")
        
        new_name = prompt(f"Full Name [{c['full_name']}]: ")
        if new_name:
            c["full_name"] = new_name
        
        new_party = prompt(f"Party [{c['party']}]: ")
        if new_party:
            c["party"] = new_party
        
        new_manifesto = prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
        if new_manifesto:
            c["manifesto"] = new_manifesto
        
        new_phone = prompt(f"Phone [{c['phone']}]: ")
        if new_phone:
            c["phone"] = new_phone
        
        new_email = prompt(f"Email [{c['email']}]: ")
        if new_email:
            c["email"] = new_email
        
        new_address = prompt(f"Address [{c['address']}]: ")
        if new_address:
            c["address"] = new_address
        
        new_exp = prompt(f"Years Experience [{c['years_experience']}]: ")
        if new_exp:
            try:
                c["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        log_action(self.store, "UPDATE_CANDIDATE", current_user["username"],
                  f"Updated candidate: {c['full_name']} (ID: {cid})")
        print()
        success(f"Candidate '{c['full_name']}' updated successfully!")
        self.store.save_data()
        pause()
        return True
    
    def delete(self, current_user) -> bool:
        """Deactivate a candidate.

        Returns True if a candidate was deactivated, False otherwise.
        """
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return False
        
        print()
        for cid, c in self.store.candidates.items():
            status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
        
        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if cid not in self.store.candidates:
            error("Candidate not found.")
            pause()
            return False
        
        # Check if candidate is in active polls
        for pid, poll in self.store.polls.items():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        error(f"Cannot delete - candidate is in active poll: {poll['title']}")
                        pause()
                        return False
        
        confirm = prompt(f"Are you sure you want to delete '{self.store.candidates[cid]['full_name']}'? (yes/no): ").lower()
        if confirm == "yes":
            deleted_name = self.store.candidates[cid]["full_name"]
            self.store.candidates[cid]["is_active"] = False
            log_action(self.store, "DELETE_CANDIDATE", current_user["username"],
                      f"Deactivated candidate: {deleted_name} (ID: {cid})")
            print()
            success(f"Candidate '{deleted_name}' has been deactivated.")
            self.store.save_data()
            pause()
            return True
        else:
            info("Deletion cancelled.")
            pause()
            return False
    
    def search(self, **kwargs):
        """Search for candidates.

        If keyword arguments are supplied, they are used for programmatic filtering.
        Supported keys: name (str), party (str), education (str), min_age (int), max_age (int).

        When called without kwargs the method presents an interactive menu and
        returns the resulting list.

        Returns a list of matching candidate dictionaries.
        """
        # programmatic mode
        if kwargs:
            results = list(self.store.candidates.values())
            name = kwargs.get("name")
            if name:
                term = name.lower()
                results = [c for c in results if term in c["full_name"].lower()]
            party = kwargs.get("party")
            if party:
                term = party.lower()
                results = [c for c in results if term in c["party"].lower()]
            education = kwargs.get("education")
            if education:
                results = [c for c in results if c["education"] == education]
            min_age = kwargs.get("min_age")
            max_age = kwargs.get("max_age")
            if min_age is not None and max_age is not None:
                results = [c for c in results if min_age <= c["age"] <= max_age]
            return results

        # interactive fallback
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)

        choice = prompt("\nChoice: ")
        results = []

        if choice == "1":
            term = prompt("Enter name to search: ").lower()
            results = [c for c in self.store.candidates.values() if term in c["full_name"].lower()]

        elif choice == "2":
            term = prompt("Enter party name: ").lower()
            results = [c for c in self.store.candidates.values() if term in c["party"].lower()]

        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(self.store.REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = self.store.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = [c for c in self.store.candidates.values() if c["education"] == edu]
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
                return []

        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = [c for c in self.store.candidates.values() if min_age <= c["age"] <= max_age]
            except ValueError:
                error("Invalid input.")
                pause()
                return []

        else:
            error("Invalid choice.")
            pause()
            return []

        if not results:
            print()
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")

        pause()
        return results
