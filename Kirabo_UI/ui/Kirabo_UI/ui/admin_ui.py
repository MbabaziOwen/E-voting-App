# ui/admin_ui.py

from ui.display import *


def admin_dashboard(admin_name):
    while True:

        clear_screen()
        header("ADMIN DASHBOARD", THEME_ADMIN)

        print(f"Logged in as: {admin_name}\n")

        subheader("Candidate Management", THEME_ADMIN)
        menu_item(1, "Create Candidate", THEME_ADMIN)
        menu_item(2, "View Candidates", THEME_ADMIN)
        menu_item(3, "Update Candidate", THEME_ADMIN)
        menu_item(4, "Delete Candidate", THEME_ADMIN)

        subheader("Voting Stations", THEME_ADMIN)
        menu_item(5, "Create Station", THEME_ADMIN)
        menu_item(6, "View Stations", THEME_ADMIN)

        subheader("Polls", THEME_ADMIN)
        menu_item(7, "Create Poll", THEME_ADMIN)
        menu_item(8, "View Polls", THEME_ADMIN)

        subheader("System", THEME_ADMIN)
        menu_item(9, "Logout", THEME_ADMIN)

        choice = prompt("\nSelect option")

        return choice
