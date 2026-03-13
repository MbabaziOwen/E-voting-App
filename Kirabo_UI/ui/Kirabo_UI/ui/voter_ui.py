# ui/voter_ui.py

from ui.display import *


def voter_dashboard(voter_name):

    while True:

        clear_screen()
        header("VOTER DASHBOARD", THEME_VOTER)

        print(f"Welcome {voter_name}\n")

        menu_item(1, "View Available Polls", THEME_VOTER)
        menu_item(2, "Cast Vote", THEME_VOTER)
        menu_item(3, "View Voting History", THEME_VOTER)
        menu_item(4, "Logout", THEME_VOTER)

        choice = prompt("\nSelect option")

        return choice
