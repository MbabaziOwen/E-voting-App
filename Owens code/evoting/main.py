import sys
import os

# Making  sure Python can find all project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage.data_store    import DataStore
from services.auth_service import AuthService
from ui.admin_ui           import AdminUI
from ui.voter_ui           import VoterUI


def main():
    """
    Application entry point.

    1. Creates one shared DataStore instance
    2. Loads any previously saved data from disk
    3. Wires all services and UI classes to that store
    4. Loops forever: show login -> route to correct dashboard -> repeat
    """

    # ── 1. Create and load the data store ───────────────────────
    store = DataStore()
    store.load()

    # ── 2. Create services and UI handlers ──────────────────────
    # All receive the SAME store instance so they share data
    auth      = AuthService(store)
    admin_ui  = AdminUI(store)
    voter_ui  = VoterUI(store)

    # ── 3. Main application loop ─────────────────────────────────
    while True:
        # Show login screen — returns (user_dict, role_string)
        # or (None, None) if login failed / user chose to exit
        user, role = auth.login()

        if role == "admin":
            # Hand control to the admin dashboard
            # Returns when the admin chooses Logout
            admin_ui.dashboard(user)

        elif role == "voter":
            # Hand control to the voter dashboard
            # Returns when the voter chooses Logout
            voter_ui.dashboard(user)

        # After logout the loop restarts and shows the login screen again


if __name__ == "__main__":
    main()