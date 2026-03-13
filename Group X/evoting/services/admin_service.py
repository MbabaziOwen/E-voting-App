# services/admin_service.py
import hashlib
import datetime
from storage.data_store import DataStore
from ui.display import (
    clear_screen, header, subheader, menu_item, prompt,
    error, success, warning, info, pause,
    table_header, table_divider, status_badge, masked_input,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, DIM, RESET,
    GREEN, RED, YELLOW
)
from utils.helpers import log_action


class AdminService:
    def __init__(self, store: DataStore):
        self.store = store

    def create(self, current_user):
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if current_user["role"] != "super_admin":
            print()
            error("Only super admins can create admin accounts.")
            pause()
            return
        print()
        username = prompt("Username: ")
        if not username:
            error("Username cannot be empty.")
            pause()
            return
        for aid, a in self.store.admins.items():
            if a["username"] == username:
                error("Username already exists.")
                pause()
                return
        full_name = prompt("Full Name: ")
        email     = prompt("Email: ")
        password  = masked_input("Password: ").strip()
        if len(password) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        menu_item(1, f"super_admin {DIM}─ Full access{RESET}",                        THEME_ADMIN)
        menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}",   THEME_ADMIN)
        menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
        menu_item(4, f"auditor {DIM}─ Read-only access{RESET}",                       THEME_ADMIN)
        role_choice = prompt("\nSelect role (1-4): ")
        role_map = {
            "1": "super_admin",
            "2": "election_officer",
            "3": "station_manager",
            "4": "auditor"
        }
        if role_choice not in role_map:
            error("Invalid role.")
            pause()
            return
        role = role_map[role_choice]
        self.store.admins[self.store.admin_id_counter] = {
            "id":         self.store.admin_id_counter,
            "username":   username,
            "password":   hashlib.sha256(password.encode()).hexdigest(),
            "full_name":  full_name,
            "email":      email,
            "role":       role,
            "created_at": str(datetime.datetime.now()),
            "is_active":  True
        }
        log_action(self.store, "CREATE_ADMIN",
                   current_user["username"],
                   f"Created admin: {username} (Role: {role})")
        print()
        success(f"Admin '{username}' created with role: {role}")
        self.store.admin_id_counter += 1
        self.store.save_data()
        pause()

    def view_all(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        table_header(
            f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
            THEME_ADMIN
        )
        table_divider(78, THEME_ADMIN)
        for aid, a in self.store.admins.items():
            active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
            print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
        print(f"\n  {DIM}Total Admins: {len(self.store.admins)}{RESET}")
        pause()

    def deactivate(self, current_user):
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        if current_user["role"] != "super_admin":
            print()
            error("Only super admins can deactivate admins.")
            pause()
            return
        print()
        for aid, a in self.store.admins.items():
            active = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if aid not in self.store.admins:
            error("Admin not found.")
            pause()
            return
        if aid == current_user["id"]:
            error("Cannot deactivate your own account.")
            pause()
            return
        if prompt(f"Deactivate '{self.store.admins[aid]['username']}'? (yes/no): ").lower() == "yes":
            self.store.admins[aid]["is_active"] = False
            log_action(self.store, "DEACTIVATE_ADMIN",
                       current_user["username"],
                       f"Deactivated admin: {self.store.admins[aid]['username']}")
            print()
            success("Admin deactivated.")
            self.store.save_data()
        pause()

    def view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        if not self.store.audit_log:
            print()
            info("No audit records.")
            pause()
            return
        print(f"\n  {DIM}Total Records: {len(self.store.audit_log)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1, "Last 20 entries",        THEME_ADMIN)
        menu_item(2, "All entries",            THEME_ADMIN)
        menu_item(3, "Filter by action type",  THEME_ADMIN)
        menu_item(4, "Filter by user",         THEME_ADMIN)
        choice  = prompt("\nChoice: ")
        entries = self.store.audit_log
        if choice == "1":
            entries = self.store.audit_log[-20:]
        elif choice == "3":
            action_types = list(set(e["action"] for e in self.store.audit_log))
            for i, at in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                at_choice = int(prompt("Select action type: "))
                entries = [e for e in self.store.audit_log
                           if e["action"] == action_types[at_choice - 1]]
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
                return
        elif choice == "4":
            uf = prompt("Enter username/card number: ")
            entries = [e for e in self.store.audit_log
                       if uf.lower() in e["user"].lower()]
        print()
        table_header(
            f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}",
            THEME_ADMIN
        )
        table_divider(100, THEME_ADMIN)
        for entry in entries:
            ac = (GREEN  if "CREATE" in entry["action"] or entry["action"] == "LOGIN"
                  else (RED    if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]
                        else (YELLOW if "UPDATE" in entry["action"] else RESET)))
            print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  "
                  f"{ac}{entry['action']:<25}{RESET} "
                  f"{entry['user']:<20} "
                  f"{DIM}{entry['details'][:50]}{RESET}")
        pause()