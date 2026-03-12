import datetime
from storage.data_store import DataStore
from ui.display import (
    prompt, error, success, warning, info, clear_screen, pause,
    header, subheader, menu_item, table_header, table_divider, status_badge,
    THEME_ADMIN, THEME_ADMIN_ACCENT, RESET, BOLD, DIM
)
from utils.helpers import log_action


class StationService:
    """Handle voting station management operations."""
    
    def __init__(self, store: DataStore):
        self.store = store
    
    def create(self, current_user):
        """Create a new voting station.

        Returns the created station dict, or None if cancelled.
        """
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        
        name = prompt("Station Name: ")
        if not name:
            error("Name cannot be empty.")
            pause()
            return None
        
        location = prompt("Location/Address: ")
        if not location:
            error("Location cannot be empty.")
            pause()
            return None
        
        region = prompt("Region/District: ")
        
        try:
            capacity = int(prompt("Voter Capacity: "))
            if capacity <= 0:
                error("Capacity must be positive.")
                pause()
                return None
        except ValueError:
            error("Invalid capacity.")
            pause()
            return None
        
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")
        
        sid = self.store.station_id_counter
        self.store.voting_stations[sid] = {
            "id": sid,
            "name": name,
            "location": location,
            "region": region,
            "capacity": capacity,
            "registered_voters": 0,
            "supervisor": supervisor,
            "contact": contact,
            "opening_time": opening_time,
            "closing_time": closing_time,
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": current_user["username"]
        }
        
        log_action(self.store, "CREATE_STATION", current_user["username"],
                  f"Created station: {name} (ID: {sid})")
        print()
        success(f"Voting Station '{name}' created! ID: {sid}")
        self.store.station_id_counter += 1
        self.store.save_data()
        pause()
        return self.store.voting_stations[sid]
    
    def view_all(self):
        """Display all voting stations and return them as a list."""
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        
        stations = list(self.store.voting_stations.values())
        if not stations:
            print()
            info("No voting stations found.")
            pause()
            return []
        
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
        table_divider(96, THEME_ADMIN)
        
        for s in stations:
            reg_count = sum(1 for v in self.store.voters.values() if v["station_id"] == s["id"])
            status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")
        
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()
        return stations
    
    def update(self, current_user) -> bool:
        """Update station information.

        Returns True if station updated, False otherwise.
        """
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        
        if not self.store.voting_stations:
            print()
            info("No stations found.")
            pause()
            return False
        
        print()
        for sid, s in self.store.voting_stations.items():
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
        
        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return False
        
        if sid not in self.store.voting_stations:
            error("Station not found.")
            pause()
            return False
        
        s = self.store.voting_stations[sid]
        print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
        info("Press Enter to keep current value\n")
        
        new_name = prompt(f"Name [{s['name']}]: ")
        if new_name:
            s["name"] = new_name
        
        new_location = prompt(f"Location [{s['location']}]: ")
        if new_location:
            s["location"] = new_location
        
        new_region = prompt(f"Region [{s['region']}]: ")
        if new_region:
            s["region"] = new_region
        
        new_capacity = prompt(f"Capacity [{s['capacity']}]: ")
        if new_capacity:
            try:
                s["capacity"] = int(new_capacity)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        new_supervisor = prompt(f"Supervisor [{s['supervisor']}]: ")
        if new_supervisor:
            s["supervisor"] = new_supervisor
        
        new_contact = prompt(f"Contact [{s['contact']}]: ")
        if new_contact:
            s["contact"] = new_contact
        
        log_action(self.store, "UPDATE_STATION", current_user["username"],
                  f"Updated station: {s['name']} (ID: {sid})")
        print()
        success(f"Station '{s['name']}' updated successfully!")
        self.store.save_data()
        pause()
        return True
    
    def delete(self, current_user) -> bool:
        """Deactivate a voting station.

        Returns True if station was deactivated, False otherwise.
        """
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        
        if not self.store.voting_stations:
            print()
            info("No stations found.")
            pause()
            return
        
        print()
        for sid, s in self.store.voting_stations.items():
            status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
        
        try:
            sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if sid not in self.store.voting_stations:
            error("Station not found.")
            pause()
            return
        
        voter_count = sum(1 for v in self.store.voters.values() if v["station_id"] == sid)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                info("Cancelled.")
                pause()
                return
        
        if prompt(f"Confirm deactivation of '{self.store.voting_stations[sid]['name']}'? (yes/no): ").lower() == "yes":
            self.store.voting_stations[sid]["is_active"] = False
            log_action(self.store, "DELETE_STATION", current_user["username"],
                      f"Deactivated station: {self.store.voting_stations[sid]['name']}")
            print()
            success(f"Station '{self.store.voting_stations[sid]['name']}' deactivated.")
            self.store.save_data()
            pause()
            return True
        else:
            info("Cancelled.")
            pause()
            return False

    def search(self, **kwargs):
        """Search voting stations.

        Supports filtering by name or region via kwargs.
        When called without args, falls back to an interactive prompt.
        Returns list of station dictionaries.
        """
        # programmatic filtering
        if kwargs:
            results = list(self.store.voting_stations.values())
            name = kwargs.get("name")
            if name:
                term = name.lower()
                results = [s for s in results if term in s["name"].lower()]
            region = kwargs.get("region")
            if region:
                term = region.lower()
                results = [s for s in results if term in s["region"].lower()]
            return results

        # interactive search
        clear_screen()
        header("SEARCH STATIONS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Region", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        results = []

        if choice == "1":
            term = prompt("Enter station name: ").lower()
            results = [s for s in self.store.voting_stations.values() if term in s["name"].lower()]
        elif choice == "2":
            term = prompt("Enter region: ").lower()
            results = [s for s in self.store.voting_stations.values() if term in s["region"].lower()]
        else:
            error("Invalid choice.")
            pause()
            return []

        if not results:
            print()
            info("No stations found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} station(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15}", THEME_ADMIN)
            table_divider(70, THEME_ADMIN)
            for s in results:
                status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
                print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {status}")
        pause()
        return results
