import datetime
import random
import string
import hashlib


def hash_password(password):
    """Return SHA256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number():
    """Generate a random 12-character voter card number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def log_action(store, action, user, details):
    """Log an action to the audit log."""
    store.audit_log.append({
        "timestamp": str(datetime.datetime.now()),
        "action": action,
        "user": user,
        "details": details
    })
