# services/poll_service.py
import datetime
from storage.data_store import DataStore
from ui.display import (
    clear_screen, header, subheader, prompt, error, success,
    warning, info, pause, menu_item, status_badge, table_header, table_divider,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, DIM, RESET,
    GREEN, YELLOW, RED, BRIGHT_YELLOW
)
from utils.helpers import log_action


class PollService:
    def __init__(self, store: DataStore):
        self.store = store

    # ── Positions ────────────────────────────────────────────────

    def create_position(self, current_user):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in ["national", "regional", "local"]:
            error("Invalid level.")
            pause()
            return
        try:
            max_winners = int(prompt("Number of winners/seats: "))
            if max_winners <= 0:
                error("Must be at least 1.")
                pause()
                return
        except ValueError:
            error("Invalid number.")
            pause()
            return
        min_cand_age = prompt(f"Minimum candidate age [{self.store.MIN_CANDIDATE_AGE}]: ")
        min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else self.store.MIN_CANDIDATE_AGE
        self.store.positions[self.store.position_id_counter] = {
            "id":               self.store.position_id_counter,
            "title":            title,
            "description":      description,
            "level":            level.capitalize(),
            "max_winners":      max_winners,
            "min_candidate_age": min_cand_age,
            "is_active":        True,
            "created_at":       str(datetime.datetime.now()),
            "created_by":       current_user["username"]
        }
        log_action(self.store, "CREATE_POSITION",
                   current_user["username"],
                   f"Created position: {title} (ID: {self.store.position_id_counter})")
        print()
        success(f"Position '{title}' created! ID: {self.store.position_id_counter}")
        self.store.position_id_counter += 1
        self.store.save_data()
        pause()

    def view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        for pid, p in self.store.positions.items():
            status = status_badge("Active", True) if p["is_active"] else status_badge("Inactive", False)
            print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")
        print(f"\n  {DIM}Total Positions: {len(self.store.positions)}{RESET}")
        pause()

    def update_position(self, current_user):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        for pid, p in self.store.positions.items():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.positions:
            error("Position not found.")
            pause()
            return
        p = self.store.positions[pid]
        print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
        info("Press Enter to keep current value\n")
        new_title = prompt(f"Title [{p['title']}]: ")
        if new_title: p["title"] = new_title
        new_desc = prompt(f"Description [{p['description'][:50]}]: ")
        if new_desc: p["description"] = new_desc
        new_level = prompt(f"Level [{p['level']}]: ")
        if new_level and new_level.lower() in ["national", "regional", "local"]:
            p["level"] = new_level.capitalize()
        new_seats = prompt(f"Seats [{p['max_winners']}]: ")
        if new_seats:
            try:
                p["max_winners"] = int(new_seats)
            except ValueError:
                warning("Keeping old value.")
        log_action(self.store, "UPDATE_POSITION",
                   current_user["username"], f"Updated position: {p['title']}")
        print()
        success("Position updated!")
        self.store.save_data()
        pause()

    def delete_position(self, current_user):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        for pid, p in self.store.positions.items():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.positions:
            error("Position not found.")
            pause()
            return
        for poll_id, poll in self.store.polls.items():
            for pp in poll.get("positions", []):
                if pp["position_id"] == pid and poll["status"] == "open":
                    error(f"Cannot delete - in active poll: {poll['title']}")
                    pause()
                    return
        if prompt(f"Confirm deactivation of '{self.store.positions[pid]['title']}'? (yes/no): ").lower() == "yes":
            self.store.positions[pid]["is_active"] = False
            log_action(self.store, "DELETE_POSITION",
                       current_user["username"],
                       f"Deactivated position: {self.store.positions[pid]['title']}")
            print()
            success("Position deactivated.")
            self.store.save_data()
        pause()

    # ── Polls ────────────────────────────────────────────────────

    def create(self, current_user):
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")
        try:
            sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd:
                error("End date must be after start date.")
                pause()
                return
        except ValueError:
            error("Invalid date format.")
            pause()
            return
        if not self.store.positions:
            error("No positions available. Create positions first.")
            pause()
            return
        subheader("Available Positions", THEME_ADMIN_ACCENT)
        active_positions = {pid: p for pid, p in self.store.positions.items() if p["is_active"]}
        if not active_positions:
            error("No active positions.")
            pause()
            return
        for pid, p in active_positions.items():
            print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
        try:
            selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll_positions = []
        for spid in selected_position_ids:
            if spid not in active_positions:
                warning(f"Position ID {spid} not found or inactive. Skipping.")
                continue
            poll_positions.append({
                "position_id":    spid,
                "position_title": self.store.positions[spid]["title"],
                "candidate_ids":  [],
                "max_winners":    self.store.positions[spid]["max_winners"]
            })
        if not poll_positions:
            error("No valid positions selected.")
            pause()
            return
        if not self.store.voting_stations:
            error("No voting stations. Create stations first.")
            pause()
            return
        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        active_stations = {sid: s for sid, s in self.store.voting_stations.items() if s["is_active"]}
        for sid, s in active_stations.items():
            print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                error("Invalid input.")
                pause()
                return
        self.store.polls[self.store.poll_id_counter] = {
            "id":               self.store.poll_id_counter,
            "title":            title,
            "description":      description,
            "election_type":    election_type,
            "start_date":       start_date,
            "end_date":         end_date,
            "positions":        poll_positions,
            "station_ids":      selected_station_ids,
            "status":           "draft",
            "total_votes_cast": 0,
            "created_at":       str(datetime.datetime.now()),
            "created_by":       current_user["username"]
        }
        log_action(self.store, "CREATE_POLL",
                   current_user["username"],
                   f"Created poll: {title} (ID: {self.store.poll_id_counter})")
        print()
        success(f"Poll '{title}' created! ID: {self.store.poll_id_counter}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
        self.store.poll_id_counter += 1
        self.store.save_data()
        pause()

    def view_all(self):
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
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cand_names = [self.store.candidates[ccid]["full_name"]
                              for ccid in pos["candidate_ids"]
                              if ccid in self.store.candidates]
                cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(self.store.polls)}{RESET}")
        pause()

    def update(self, current_user):
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return
        poll = self.store.polls[pid]
        if poll["status"] == "open":
            error("Cannot update an open poll. Close it first.")
            pause()
            return
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            error("Cannot update a poll with votes.")
            pause()
            return
        print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
        info("Press Enter to keep current value\n")
        new_title = prompt(f"Title [{poll['title']}]: ")
        if new_title: poll["title"] = new_title
        new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
        if new_desc: poll["description"] = new_desc
        new_type = prompt(f"Election Type [{poll['election_type']}]: ")
        if new_type: poll["election_type"] = new_type
        new_start = prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                datetime.datetime.strptime(new_start, "%Y-%m-%d")
                poll["start_date"] = new_start
            except ValueError:
                warning("Invalid date, keeping old value.")
        new_end = prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                datetime.datetime.strptime(new_end, "%Y-%m-%d")
                poll["end_date"] = new_end
            except ValueError:
                warning("Invalid date, keeping old value.")
        log_action(self.store, "UPDATE_POLL",
                   current_user["username"], f"Updated poll: {poll['title']}")
        print()
        success("Poll updated!")
        self.store.save_data()
        pause()

    def delete(self, current_user):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for pid, poll in self.store.polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return
        if self.store.polls[pid]["status"] == "open":
            error("Cannot delete an open poll. Close it first.")
            pause()
            return
        if self.store.polls[pid]["total_votes_cast"] > 0:
            warning(f"This poll has {self.store.polls[pid]['total_votes_cast']} votes recorded.")
        if prompt(f"Confirm deletion of '{self.store.polls[pid]['title']}'? (yes/no): ").lower() == "yes":
            deleted_title = self.store.polls[pid]["title"]
            del self.store.polls[pid]
            self.store.votes = [v for v in self.store.votes if v["poll_id"] != pid]
            log_action(self.store, "DELETE_POLL",
                       current_user["username"], f"Deleted poll: {deleted_title}")
            print()
            success(f"Poll '{deleted_title}' deleted.")
            self.store.save_data()
        pause()

    def open_close(self, current_user):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return
        poll = self.store.polls[pid]
        if poll["status"] == "draft":
            if not any(pos["candidate_ids"] for pos in poll["positions"]):
                error("Cannot open - no candidates assigned.")
                pause()
                return
            if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                log_action(self.store, "OPEN_POLL",
                           current_user["username"], f"Opened poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now OPEN for voting!")
                self.store.save_data()
        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                poll["status"] = "closed"
                log_action(self.store, "CLOSE_POLL",
                           current_user["username"], f"Closed poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now CLOSED.")
                self.store.save_data()
        elif poll["status"] == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                log_action(self.store, "REOPEN_POLL",
                           current_user["username"], f"Reopened poll: {poll['title']}")
                print()
                success("Poll reopened!")
                self.store.save_data()
        pause()

    def assign_candidates(self, current_user):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return
        print()
        for pid, poll in self.store.polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return
        poll = self.store.polls[pid]
        if poll["status"] == "open":
            error("Cannot modify candidates of an open poll.")
            pause()
            return
        for pos in poll["positions"]:
            subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            current_cands = [f"{ccid}: {self.store.candidates[ccid]['full_name']}"
                             for ccid in pos["candidate_ids"]
                             if ccid in self.store.candidates]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                info("No candidates assigned yet.")
            active_candidates = {cid: c for cid, c in self.store.candidates.items()
                                  if c["is_active"] and c["is_approved"]}
            pos_data = self.store.positions.get(pos["position_id"], {})
            min_age = pos_data.get("min_candidate_age", self.store.MIN_CANDIDATE_AGE)
            eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
            if not eligible:
                info("No eligible candidates found.")
                continue
            subheader("Available Candidates", THEME_ADMIN)
            for cid, c in eligible.items():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_cand_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    valid_ids = []
                    for ncid in new_cand_ids:
                        if ncid in eligible:
                            valid_ids.append(ncid)
                        else:
                            warning(f"Candidate {ncid} not eligible. Skipping.")
                    pos["candidate_ids"] = valid_ids
                    success(f"{len(valid_ids)} candidate(s) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        log_action(self.store, "ASSIGN_CANDIDATES",
                   current_user["username"],
                   f"Updated candidates for poll: {poll['title']}")
        self.store.save_data()
        pause()