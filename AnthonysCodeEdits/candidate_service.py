"""Legacy wrappers for candidate operations.

These functions exist only for compatibility with earlier code. They delegate
all work to the new, class‑based service implementation and therefore no
longer read globals or call ``save_data()``/``log_action`` directly.  The
wrapper signature takes an explicit ``store`` instance so that the
substitution rule is preserved.
"""

from AnthonysCodeEdits.services.candidate_service import CandidateService


def create_candidate(store, current_user=None):
    """Create a candidate using the supplied DataStore.

    ``current_user`` defaults to ``store.current_user`` if omitted.  Returns the
    new candidate dict or ``None`` on failure.
    """
    return CandidateService(store).create(current_user or store.current_user)


def view_all_candidates(store):
    """Delegate to ``CandidateService.view_all`` and return its list."""
    return CandidateService(store).view_all()


def update_candidate(store, current_user=None):
    """Delegate to ``CandidateService.update``. Returns boolean."""
    return CandidateService(store).update(current_user or store.current_user)


def delete_candidate(store, current_user=None):
    """Delegate to ``CandidateService.delete``. Returns boolean."""
    return CandidateService(store).delete(current_user or store.current_user)


def search_candidates(store, **kwargs):
    """Delegate to ``CandidateService.search``. Passes through kwargs."""
    return CandidateService(store).search(**kwargs)
