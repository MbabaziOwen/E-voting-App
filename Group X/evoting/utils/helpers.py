import hashlib
import random
import string
import os
import datetime


def hash_password(password: str) -> str:
    """Convert plain text password to SHA-256 hash."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number() -> str:
    """Generate a random 12-character voter card number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """Wait for the user to press Enter before continuing."""
    input("\n  Press Enter to continue...")


def log_action(store, action: str, user: str, details: str):
    """
    Append an audit record to the audit_log list in the DataStore.

    Parameters:
        store   : DataStore instance containing the audit_log
        action  : short action name e.g. "LOGIN", "CREATE_CANDIDATE"
        user    : username or voter card number of the person acting
        details : human-readable description of what happened
    """
    store.audit_log.append({
        "timestamp": str(datetime.datetime.now()),
        "action":    action,
        "user":      user,
        "details":   details
    })