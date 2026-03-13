"""Legacy authentication helpers delegating to the new AuthService class.

Utilities such as ``hash_password`` remain for compatibility, but login and
registration functions simply forward to the class-based service using an
explicit ``store`` argument.  No global state is accessed directly.
"""

import hashlib
import random
import string

from AnthonysCodeEdits.class_services.auth_service import AuthService


# --- utility helpers ---

def hash_password(password):
    """Return a SHA256 hash of the provided password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number():
    """Produce a pseudo‑random 12‑character voter card ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


# --- authentication / registration wrappers ---

def login(store, username=None, password=None):
    """Delegate to ``AuthService.login``.

    ``username``/``password`` may be provided for non‑interactive use.
    Returns ``(user, role)`` tuple.
    """
    return AuthService(store).login(username=username, password=password)


def register_voter(store, **kwargs):
    """Delegate to ``AuthService.register``.

    All registration fields may be supplied as keyword arguments.  Returns the
    new voter dict or ``None`` on failure.
    """
    return AuthService(store).register(**kwargs)
