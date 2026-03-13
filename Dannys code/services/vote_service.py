from typing import Dict, Any


class VoteService:

    def cast_vote(self, current_user: Dict[str, Any]) -> bool:
        # Exact logic from cast_vote() - SPECIAL TRIPLE UPDATE REQUIRED
        from ..e_voting_console_app import (
            clear_screen, header, prompt, error, info, success, pause, warning, THEME_VOTER,
            THEME_VOTER_ACCENT, BRIGHT_YELLOW, GREEN, GRAY, BOLD, BG_GREEN, BLACK, RESET
        )
        from datetime import datetime
        import hashlib

        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        
        open_polls = {pid: p for pid, p in self.store.polls.items() if p["status"] == "open"}
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return False
        
        available_polls = {}
        for pid, poll in open_polls.items():
            if (pid not in current_user.get("has_voted_in", []) and 
                current_user["station_id"] in poll["station_ids"]):
                available_polls[pid] = poll
        
        if not available_polls:
            print()
            info("No available polls to vote in.")
            pause()
            return False
        
        print("Available Polls:")
        for pid, poll in available_polls.items():
            print(f"  {THEME_VOTER}{pid}. {poll['title']} ({poll['election_type']})")
        
        try:
            pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if pid not in available_polls:
            error("Invalid poll selection.")
            pause()
            return False
        
        poll = self.store.polls[pid]
        print()
        header(f"Voting: {poll['title']}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")
        
        my_votes = []
        for pos in poll["positions"]:
            print(f"\n{pos['position_title']}")
            if not pos["candidate_ids"]:
                info("No candidates for this position.")
                continue
            
            for idx, ccid in enumerate(pos["candidate_ids"], 1):
                if ccid in self.store.candidates:
                    c = self.store.candidates[ccid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}. {c['full_name']} ({c['party']})")
                    print(f"       Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs")
                    if c.get("manifesto"):
                        print(f"       {c['manifesto'][:80]}...")
            
            print(f"    {GRAY}{BOLD}0. Abstain / Skip{GRAY}")
            try:
                vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
            except ValueError:
                warning("Invalid input. Skipping.")
                vote_choice = 0
            
            if vote_choice == 0:
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": None,
                    "abstained": True
                })
            elif 1 <= vote_choice <= len(pos["candidate_ids"]):
                selected_cid = pos["candidate_ids"][vote_choice - 1]
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": selected_cid,
                    "candidate_name": self.store.candidates[selected_cid]["full_name"],
                    "abstained": False
                })
            else:
                warning("Invalid choice. Marking as abstain.")
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": None,
                    "abstained": True
                })
        
        print("\nVOTE SUMMARY:")
        for mv in my_votes:
            if mv["abstained"]:
                print(f"  {mv['position_title']}: {GRAY}ABSTAINED")
            else:
                print(f"  {mv['position_title']}: {mv['candidate_name']}")
        
        print()
        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            info("Vote cancelled.")
            pause()
            return False
        
        # SPECIAL TRIPLE UPDATE REQUIRED
        vote_timestamp = str(datetime.now())
        vote_hash = hashlib.sha256(f"{current_user['id']}{pid}{vote_timestamp}".encode()).hexdigest()[:16]
        
        for mv in my_votes:
            self.store.votes.append({
                "vote_id": vote_hash + str(mv["position_id"]),
                "poll_id": pid,
                "position_id": mv["position_id"],
                "candidate_id": mv["candidate_id"],
                "voter_id": current_user["id"],
                "station_id": current_user["station_id"],
                "timestamp": vote_timestamp,
                "abstained": mv["abstained"]
            })
        
        # Update poll total
        self.store.polls[pid]["total_votes_cast"] += 1
        
        # Update voter in store AND current_user (shared reference)
        current_user["has_voted_in"].append(pid)
        for vid, v in self.store.voters.items():
            if v["id"] == current_user["id"]:
                v["has_voted_in"].append(pid)
                break
        
        self.store.save()
        self.store.log_action("CAST_VOTE", current_user["voter_card_number"], 
                            f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
        
        print()
        success("Your vote has been recorded successfully!")
        print(f"  Vote Reference: {BRIGHT_YELLOW}{vote_hash}")
        print(f"  Thank you for participating in the democratic process!")
        pause()
        return True

    def view_results(self):
        # Exact logic from view_poll_results()
        from ..e_voting_console_app import (
            clear_screen, header, prompt, error, info, pause, THEME_ADMIN, THEME_ADMIN_ACCENT,
            status_badge, BOLD, GREEN, RED, YELLOW, DIM, BG_GREEN, BLACK, RESET, GRAY
        )
        
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{pid}. {poll['title']} {sc}({poll['status']})")
        
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
        print()
        header(f"RESULTS: {poll['title']}", THEME_ADMIN)
        sc = GREEN if poll['status'] == 'open' else RED
        print(f"  Status: {sc}{BOLD}{poll['status'].upper()}{sc} │ Votes: {BOLD}{poll['total_votes_cast']}")
        
        total_eligible = sum(1 for v in self.store.voters.values() 
                           if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"])
        turnout = (poll['total_votes_cast'] / total_eligible * 100) if total_eligible > 0 else 0
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  Eligible: {total_eligible} │ Turnout: {tc}{BOLD}{turnout:.1f}%")
        
        for pos in poll["positions"]:
            print(f"\n{pos['position_title']} (Seats: {pos['max_winners']})")
            vote_counts = {}
            abstain_count = 0
            total_pos = 0
            
            for v in self.store.votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    total_pos += 1
                    if v["abstained"]:
                        abstain_count += 1
                    else:
                        vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = self.store.candidates.get(cid, {})
                pct = (count / total_pos * 100) if total_pos > 0 else 0
                bl = int(pct / 2)
                bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')} ({cand.get('party', '?')})")
                print(f"       {bar} {BOLD}{count} ({pct:.1f}%){winner}")
            
            if abstain_count > 0:
                print(f"    Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%)")
            if not vote_counts:
                info("    No votes recorded for this position.")
        pause()

    def view_statistics(self):
        # Exact logic from view_detailed_statistics()
        from ..e_voting_console_app import (
            clear_screen, header, subheader, THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, GREEN, YELLOW, RED, DIM, RESET, pause
        )
        
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)
        
        print("\nSYSTEM OVERVIEW:")
        tc = len(self.store.candidates)
        ac = sum(1 for c in self.store.candidates.values() if c["is_active"])
        tv = len(self.store.voters)
        vv = sum(1 for v in self.store.voters.values() if v["is_verified"])
        av = sum(1 for v in self.store.voters.values() if v["is_active"])
        ts = len(self.store.voting_stations)
        ast = sum(1 for s in self.store.voting_stations.values() if s["is_active"])
        tp = len(self.store.polls)
        op = sum(1 for p in self.store.polls.values() if p["status"] == "open")
        cp = sum(1 for p in self.store.polls.values() if p["status"] == "closed")
        dp = sum(1 for p in self.store.polls.values() if p["status"] == "draft")
        
        print(f"  Candidates:  {tc} (Active: {ac})")
        print(f"  Voters:      {tv} (Verified: {vv}, Active: {av})")
        print(f"  Stations:    {ts} (Active: {ast})")
        print(f"  Polls:       {tp} (Open: {op}, Closed: {cp}, Draft: {dp})")
        print(f"  Total Votes: {len(self.store.votes)}")
        
        print("\nVOTER DEMOGRAPHICS:")
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in self.store.voters.values():
            g = v.get("gender", "?")
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.get("age", 0)
            if age <= 25: age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else: age_groups["65+"] += 1
        
        for g, count in gender_counts.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        
        print(f"\n{BOLD}Age Distribution:{RESET}")
        for group, count in age_groups.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {'█' * int(pct / 2)}")
        
        print("\nSTATION LOAD:")
        for sid, s in self.store.voting_stations.items():
            vc = sum(1 for v in self.store.voters.values() if v["station_id"] == sid)
            lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
        
        print("\nCANDIDATE PARTY DISTRIBUTION:")
        party_counts = {}
        for c in self.store.candidates.values():
            if c["is_active"]:
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
        
        print("\nCANDIDATE EDUCATION LEVELS:")
        edu_counts = {}
        for c in self.store.candidates.values():
            if c["is_active"]:
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
        for edu, count in edu_counts.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        
        pause()

    def station_wise_results(self):
        # Exact logic from station_wise_results()
        from ..e_voting_console_app import (
            clear_screen, header, subheader, prompt, error, info, pause, THEME_ADMIN, BRIGHT_WHITE, BOLD, GREEN, YELLOW, RED, DIM, RESET
        )
        
        clear_screen()
        header("STATION-WISE RESULTS", THEME_ADMIN)
        
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        
        print()
        for pid, poll in self.store.polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{pid}. {poll['title']} {sc}({poll['status']})")
        
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
        print()
        header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
        
        for sid in poll["station_ids"]:
            if sid not in self.store.voting_stations:
                continue
            station = self.store.voting_stations[sid]
            subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
            
            station_votes = [v for v in self.store.votes if v["poll_id"] == pid and v["station_id"] == sid]
            svc = len(set(v["voter_id"] for v in station_votes))
            ras = sum(1 for v in self.store.voters.values() 
                     if v["station_id"] == sid and v["is_verified"] and v["is_active"])
            st = (svc / ras * 100) if ras > 0 else 0
            tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
            print(f"  Registered: {ras} │ Voted: {svc} │ Turnout: {tc}{BOLD}{st:.1f}%")
            
            for pos in poll["positions"]:
                print(f"    ▸ {pos['position_title']}:")
                pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v["abstained"]:
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                
                total = sum(vc.values()) + ac
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = self.store.candidates.get(cid, {})
                    pct = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.get('full_name', '?')} ({cand.get('party', '?')}): {BOLD}{count} ({pct:.1f}%)")
                
                if ac > 0:
                    print(f"      Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%)")
        pause()

