from typing import Dict, Any


class PollService:
    

    def create(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from create_poll()
        from ..e_voting_console_app import clear_screen, header, prompt, error, success, pause, info, warning  # UI imports
        
        clear_screen()
        header("CREATE POLL / ELECTION", 'THEME_ADMIN')
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return False
        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")
        try:
            from datetime import datetime
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd:
                error("End date must be after start date.")
                pause()
                return False
        except ValueError:
            error("Invalid date format.")
            pause()
            return False
        
        if not self.store.positions:
            error("No positions available. Create positions first.")
            pause()
            return False
        
        active_positions = {pid: p for pid, p in self.store.positions.items() if p["is_active"]}
        if not active_positions:
            error("No active positions.")
            pause()
            return False
        
        print("Available Positions:")
        for pid, p in active_positions.items():
            print(f"    {pid}. {p['title']} ({p['level']}) - {p['max_winners']} seat(s)")
        
        try:
            selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        poll_positions = []
        for spid in selected_position_ids:
            if spid in active_positions:
                poll_positions.append({
                    "position_id": spid,
                    "position_title": self.store.positions[spid]["title"],
                    "candidate_ids": [],
                    "max_winners": self.store.positions[spid]["max_winners"]
                })
            else:
                warning(f"Position ID {spid} not found or inactive. Skipping.")
        
        if not poll_positions:
            error("No valid positions selected.")
            pause()
            return False
        
        if not self.store.voting_stations:
            error("No voting stations. Create stations first.")
            pause()
            return False
        
        active_stations = {sid: s for sid, s in self.store.voting_stations.items() if s["is_active"]}
        print("Available Voting Stations:")
        for sid, s in active_stations.items():
            print(f"    {sid}. {s['name']} ({s['location']})")
        
        use_all = prompt("\nUse all active stations? (yes/no): ").lower() == "yes"
        if use_all:
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                error("Invalid input.")
                pause()
                return False
        
        self.store.polls[self.store.poll_id_counter] = {
            "id": self.store.poll_id_counter,
            "title": title,
            "description": description,
            "election_type": election_type,
            "start_date": start_date,
            "end_date": end_date,
            "positions": poll_positions,
            "station_ids": selected_station_ids,
            "status": "draft",
            "total_votes_cast": 0,
            "created_at": str(datetime.now()),
            "created_by": current_user["username"]
        }
        self.store.poll_id_counter += 1
        self.store.log_action("CREATE_POLL", current_user["username"], f"Created poll: {title}")
        print()
        success(f"Poll '{title}' created! ID: {self.store.polls[self.store.poll_id_counter - 1]['id']}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
        self.store.save()
        pause()
        return True

    def view_all(self):
        # Exact logic from view_all_polls()
        from ..e_voting_console_app import clear_screen, header, BOLD, THEME_ADMIN, DIM, GREEN, YELLOW, RED, pause, info, RESET
        
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc} {poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cand_names = [self.store.candidates.get(ccid, {}).get("full_name", "Unknown") for ccid in pos.get("candidate_ids", [])]
                cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN}▸{RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(self.store.polls)}{RESET}")
        pause()

    def update(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from update_poll()
        from ..e_voting_console_app import clear_screen, header, prompt, info, success, error, pause, warning, THEME_ADMIN, BOLD, GREEN, YELLOW, RED, RESET
        
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return False
        
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{pid}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return False
        
        poll = self.store.polls[pid]
        if poll["status"] == "open":
            error("Cannot update an open poll. Close it first.")
            pause()
            return False
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            error("Cannot update a poll with votes.")
            pause()
            return False
        
        print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
        print("Press Enter to keep current value\n")
        
        new_title = prompt(f"Title [{poll['title']}]: ")
        if new_title: poll["title"] = new_title
        new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
        if new_desc: poll["description"] = new_desc
        new_type = prompt(f"Election Type [{poll['election_type']}]: ")
        if new_type: poll["election_type"] = new_type
        new_start = prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                from datetime import datetime
                datetime.strptime(new_start, "%Y-%m-%d")
                poll["start_date"] = new_start
            except ValueError:
                warning("Invalid date, keeping old value.")
        new_end = prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                from datetime import datetime
                datetime.strptime(new_end, "%Y-%m-%d")
                poll["end_date"] = new_end
            except ValueError:
                warning("Invalid date, keeping old value.")
        
        self.store.log_action("UPDATE_POLL", current_user["username"], f"Updated poll: {poll['title']}")
        print()
        success("Poll updated!")
        self.store.save()
        pause()
        return True

    def delete(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from delete_poll()
        from ..e_voting_console_app import clear_screen, header, prompt, info, error, success, pause, warning, THEME_ADMIN, DIM, RESET
        
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return False
        
        print()
        for pid, poll in self.store.polls.items():
            print(f"  {THEME_ADMIN}{pid}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return False
        
        if self.store.polls[pid]["status"] == "open":
            error("Cannot delete an open poll. Close it first.")
            pause()
            return False
        
        if self.store.polls[pid]["total_votes_cast"] > 0:
            warning(f"This poll has {self.store.polls[pid]['total_votes_cast']} votes cast.")
        
        if prompt(f"Confirm deletion of '{self.store.polls[pid]['title']}'? (yes/no): ").lower() == "yes":
            deleted_title = self.store.polls[pid]["title"]
            del self.store.polls[pid]
            self.store.votes = [v for v in self.store.votes if v["poll_id"] != pid]
            self.store.log_action("DELETE_POLL", current_user["username"], f"Deleted poll: {deleted_title}")
            print()
            success(f"Poll '{deleted_title}' deleted.")
            self.store.save()
            pause()
            return True
        return False

    def open_close(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from open_close_poll()
        from ..e_voting_console_app import clear_screen, header, prompt, error, success, info, pause, THEME_ADMIN, GREEN, YELLOW, RED, BOLD, RESET
        
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return False
        
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{pid}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
        
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return False
        
        poll = self.store.polls[pid]
        from datetime import datetime
        if poll["status"] == "draft":
            has_candidates = any(pos["candidate_ids"] for pos in poll["positions"])
            if not has_candidates:
                error("Cannot open - no candidates assigned.")
                pause()
                return False
            if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                self.store.log_action("OPEN_POLL", current_user["username"], f"Opened poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now OPEN for voting!")
                self.store.save()
        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                poll["status"] = "closed"
                self.store.log_action("CLOSE_POLL", current_user["username"], f"Closed poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now CLOSED.")
                self.store.save()
        elif poll["status"] == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                self.store.log_action("REOPEN_POLL", current_user["username"], f"Reopened poll: {poll['title']}")
                print()
                success("Poll reopened!")
                self.store.save()
        pause()
        return True

    def assign_candidates(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from assign_candidates_to_poll()
        from ..e_voting_console_app import clear_screen, header, prompt, info, error, success, warning, pause, THEME_ADMIN, THEME_ADMIN_ACCENT, GREEN, DIM, RESET
        
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        if not self.store.polls:
            info("No polls found.")
            pause()
            return False
        if not self.store.candidates:
            info("No candidates found.")
            pause()
            return False
        
        print()
        for pid, poll in self.store.polls.items():
            print(f"  {THEME_ADMIN}{pid}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return False
        
        poll = self.store.polls[pid]
        if poll["status"] == "open":
            error("Cannot modify candidates of an open poll.")
            pause()
            return False
        
        for i, pos in enumerate(poll["positions"]):
            print(f"\nPosition: {pos['position_title']}")
            current_cands = [f"{ccid}: {self.store.candidates.get(ccid, {}).get('full_name', 'Unknown')}" for ccid in pos["candidate_ids"]]
            if current_cands:
                print(f"  Current: {', '.join(current_cands)}")
            else:
                info("No candidates assigned yet.")
            
            active_candidates = {cid: c for cid, c in self.store.candidates.items() if c["is_active"] and c["is_approved"]}
            pos_data = self.store.positions.get(pos["position_id"], {})
            min_age = pos_data.get("min_candidate_age", 25)
            eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
            
            if not eligible:
                info("No eligible candidates found.")
                continue
            
            print("Available Candidates:")
            for cid, c in eligible.items():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
                print(f"    {cid}. {c['full_name']} ({c['party']}) - Age: {c['age']}, Edu: {c['education']}{marker}")
            
            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_cand_ids_str = prompt("Enter Candidate IDs (comma-separated): ")
                    new_cand_ids = [int(x.strip()) for x in new_cand_ids_str.split(",")]
                    valid_ids = [ncid for ncid in new_cand_ids if ncid in eligible]
                    for ncid in new_cand_ids:
                        if ncid not in eligible:
                            warning(f"Candidate {ncid} not eligible. Skipping.")
                    pos["candidate_ids"] = valid_ids
                    success(f"{len(valid_ids)} candidate(s) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        
        self.store.log_action("ASSIGN_CANDIDATES", current_user["username"], f"Updated candidates for poll: {poll['title']}")
        self.store.save()
        pause()
        return True

