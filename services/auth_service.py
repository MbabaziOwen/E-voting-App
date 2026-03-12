"""Legacy auth helpers in root services package.

These simply forward to the class-based implementation in
``AnthonysCodeEdits.services.auth_service`` and thus never touch global
state or call ``save_data``/``log_action`` directly. The module also exposes
the original utility functions for compatibility.
"""

import hashlib
import random
import string

from AnthonysCodeEdits.services.auth_service import AuthService


def hash_password(password):
    """Return a SHA256 hash of the provided password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number():
    """Produce a pseudo‑random 12‑character voter card ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def login(store, username=None, password=None):
    """Delegate to ``AuthService.login``.

    ``username``/``password`` may be provided for programmatic use.
    """
    return AuthService(store).login(username=username, password=password)


def register_voter(store, **kwargs):
    """Delegate voter registration to the service.

    Keyword arguments correspond to form fields.
    """
    return AuthService(store).register(**kwargs)
