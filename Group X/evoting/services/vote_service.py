# services/vote_service.py
import hashlib
import datetime
from storage.data_store import DataStore
from ui.display import (
    clear_screen, header, subheader, prompt,
    error, success, warning, info, pause, menu_item,
    status_badge, table_header, table_divider,
    THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER, THEME_VOTER_ACCENT,
    BOLD, DIM, RESET, ITALIC, GRAY,
    GREEN, RED, YELLOW, BLACK,
    BRIGHT_WHITE, BRIGHT_YELLOW, BRIGHT_GREEN, BRIGHT_CYAN,
    BG_GREEN
)
from utils.helpers import log_action


class VoteService:
    def __init__(self, store: DataStore):
        self.store = store

    def view_open_polls(self, current_user):
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        open_polls = {pid: p for pid, p in self.store.polls.items() if p["status"] == "open"}
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return
        for pid, poll in open_polls.items():
            already_voted = pid in current_user.get("has_voted_in", [])
            vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
            for pos in poll["positions"]:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for ccid in pos["candidate_ids"]:
                    if ccid in self.store.candidates:
                        c = self.store.candidates[ccid]
                        print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
        pause()

    def cast_vote(self, current_user):
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        open_polls = {pid: p for pid, p in self.store.polls.items() if p["status"] == "open"}
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return
        available_polls = {}
        for pid, poll in open_polls.items():
            if (pid not in current_user.get("has_voted_in", []) and
                    current_user["station_id"] in poll["station_ids"]):
                available_polls[pid] = poll
        if not available_polls:
            print()
            info("No available polls to vote in.")
            pause()
            return
        subheader("Available Polls", THEME_VOTER_ACCENT)
        for pid, poll in available_polls.items():
            print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
        try:
            pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in available_polls:
            error("Invalid poll selection.")
            pause()
            return
        poll = self.store.polls[pid]
        print()
        header(f"Voting: {poll['title']}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")
        my_votes = []
        for pos in poll["positions"]:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            if not pos["candidate_ids"]:
                info("No candidates for this position.")
                continue
            for idx, ccid in enumerate(pos["candidate_ids"], 1):
                if ccid in self.store.candidates:
                    c = self.store.candidates[ccid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                    print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                    if c["manifesto"]:
                        print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
            try:
                vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
            except ValueError:
                warning("Invalid input. Skipping.")
                vote_choice = 0
            if vote_choice == 0:
                my_votes.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   None,
                    "abstained":      True
                })
            elif 1 <= vote_choice <= len(pos["candidate_ids"]):
                selected_cid = pos["candidate_ids"][vote_choice - 1]
                my_votes.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   selected_cid,
                    "candidate_name": self.store.candidates[selected_cid]["full_name"],
                    "abstained":      False
                })
            else:
                warning("Invalid choice. Marking as abstain.")
                my_votes.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   None,
                    "abstained":      True
                })
        subheader("VOTE SUMMARY", BRIGHT_WHITE)
        for mv in my_votes:
            if mv["abstained"]:
                print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
        print()
        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            info("Vote cancelled.")
            pause()
            return
        vote_timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{current_user['id']}{pid}{vote_timestamp}".encode()
        ).hexdigest()[:16]
        for mv in my_votes:
            self.store.votes.append({
                "vote_id":      vote_hash + str(mv["position_id"]),
                "poll_id":      pid,
                "position_id":  mv["position_id"],
                "candidate_id": mv["candidate_id"],
                "voter_id":     current_user["id"],
                "station_id":   current_user["station_id"],
                "timestamp":    vote_timestamp,
                "abstained":    mv["abstained"]
            })
        # Triple update — all three must happen
        self.store.polls[pid]["total_votes_cast"] += 1
        current_user["has_voted_in"].append(pid)
        for vid, v in self.store.voters.items():
            if v["id"] == current_user["id"]:
                v["has_voted_in"].append(pid)
                break
        log_action(self.store.audit_log, "CAST_VOTE",
                   current_user["voter_card_number"],
                   f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
        print()
        success("Your vote has been recorded successfully!")
        print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
        print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
        self.store.save()
        pause()

    def view_voting_history(self, current_user):
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        voted_polls = current_user.get("has_voted_in", [])
        if not voted_polls:
            print()
            info("You have not voted in any polls yet.")
            pause()
            return
        print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
        for pid in voted_polls:
            if pid in self.store.polls:
                poll = self.store.polls[pid]
                sc = GREEN if poll['status'] == 'open' else RED
                print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
                print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
                for vr in [v for v in self.store.votes
                           if v["poll_id"] == pid and v["voter_id"] == current_user["id"]]:
                    pos_title = next(
                        (pos["position_title"] for pos in poll.get("positions", [])
                         if pos["position_id"] == vr["position_id"]), "Unknown"
                    )
                    if vr["abstained"]:
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                    else:
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}"
                              f"{self.store.candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
                print()
        pause()

    def view_closed_results(self, current_user):
        clear_screen()
        header("ELECTION RESULTS", THEME_VOTER)
        closed_polls = {pid: p for pid, p in self.store.polls.items() if p["status"] == "closed"}
        if not closed_polls:
            print()
            info("No closed polls with results.")
            pause()
            return
        for pid, poll in closed_polls.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                subheader(pos['position_title'], THEME_VOTER_ACCENT)
                vote_counts  = {}
                abstain_count = 0
                for v in self.store.votes:
                    if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                        if v["abstained"]:
                            abstain_count += 1
                        else:
                            vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
                total = sum(vote_counts.values()) + abstain_count
                for rank, (cid, count) in enumerate(
                        sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                    cand = self.store.candidates.get(cid, {})
                    pct  = (count / total * 100) if total > 0 else 0
                    bar  = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                    print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                if abstain_count > 0:
                    print(f"    {GRAY}Abstained: {abstain_count} "
                          f"({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
        pause()

    def view_results(self):
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
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
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
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
        total_eligible = sum(1 for v in self.store.voters.values()
                             if v["is_verified"] and v["is_active"]
                             and v["station_id"] in poll["station_ids"])
        turnout = (poll['total_votes_cast'] / total_eligible * 100) if total_eligible > 0 else 0
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
        for pos in poll["positions"]:
            subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
            vote_counts   = {}
            abstain_count = 0
            total_pos     = 0
            for v in self.store.votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    total_pos += 1
                    if v["abstained"]:
                        abstain_count += 1
                    else:
                        vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            for rank, (cid, count) in enumerate(
                    sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = self.store.candidates.get(cid, {})
                pct  = (count / total_pos * 100) if total_pos > 0 else 0
                bl   = int(pct / 2)
                bar  = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} "
                      f"({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
            if not vote_counts:
                info("    No votes recorded for this position.")
        pause()

    def view_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)
        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        tc  = len(self.store.candidates)
        ac  = sum(1 for c in self.store.candidates.values() if c["is_active"])
        tv  = len(self.store.voters)
        vv  = sum(1 for v in self.store.voters.values() if v["is_verified"])
        av  = sum(1 for v in self.store.voters.values() if v["is_active"])
        ts  = len(self.store.voting_stations)
        ast = sum(1 for s in self.store.voting_stations.values() if s["is_active"])
        tp  = len(self.store.polls)
        op  = sum(1 for p in self.store.polls.values() if p["status"] == "open")
        cp  = sum(1 for p in self.store.polls.values() if p["status"] == "closed")
        dp  = sum(1 for p in self.store.polls.values() if p["status"] == "draft")
        print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, "
              f"{RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(self.store.votes)}")
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in self.store.voters.values():
            g = v.get("gender", "?")
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.get("age", 0)
            if age <= 25:   age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else:           age_groups["65+"]   += 1
        for g, count in gender_counts.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in age_groups.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for sid, s in self.store.voting_stations.items():
            vc = sum(1 for v in self.store.voters.values() if v["station_id"] == sid)
            lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        party_counts = {}
        for c in self.store.candidates.values():
            if c["is_active"]:
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        edu_counts = {}
        for c in self.store.candidates.values():
            if c["is_active"]:
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
        for edu, count in edu_counts.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def station_wise_results(self):
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
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
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
            station_votes = [v for v in self.store.votes
                             if v["poll_id"] == pid and v["station_id"] == sid]
            svc = len(set(v["voter_id"] for v in station_votes))
            ras = sum(1 for v in self.store.voters.values()
                      if v["station_id"] == sid and v["is_verified"] and v["is_active"])
            st  = (svc / ras * 100) if ras > 0 else 0
            tc  = GREEN if st > 50 else (YELLOW if st > 25 else RED)
            print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
            for pos in poll["positions"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
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
                    pct  = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0:
                    print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
        pause()