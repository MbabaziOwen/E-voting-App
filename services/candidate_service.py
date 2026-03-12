"""Root-package candidate functions kept for backward compatibility.

Each simply invokes the `CandidateService` class in the AnthonysCodeEdits
sub‑package so that no global state is accessed here.
"""

from AnthonysCodeEdits.services.candidate_service import CandidateService


def create_candidate(store, current_user=None):
    return CandidateService(store).create(current_user or store.current_user)


def view_all_candidates(store):
    return CandidateService(store).view_all()


def update_candidate(store, current_user=None):
    return CandidateService(store).update(current_user or store.current_user)


def delete_candidate(store, current_user=None):
    return CandidateService(store).delete(current_user or store.current_user)


def search_candidates(store, **kwargs):
    return CandidateService(store).search(**kwargs)
