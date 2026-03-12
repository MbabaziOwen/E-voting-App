"""Legacy voting-station helpers rewritten as tiny delegators.

Old callers that imported these functions can continue to do so; the
actual work is performed by ``StationService`` so there are no direct global
accesses or raw ``save_data`` calls here.
"""

from AnthonysCodeEdits.services.station_service import StationService


def create_voting_station(store, current_user=None):
    """Wrapper for ``StationService.create``."""
    return StationService(store).create(current_user or store.current_user)


def view_all_stations(store):
    """Return list of all stations via service."""
    return StationService(store).view_all()


def update_station(store, current_user=None):
    """Wrapper for update; returns bool."""
    return StationService(store).update(current_user or store.current_user)


def delete_station(store, current_user=None):
    """Wrapper for delete; returns bool."""
    return StationService(store).delete(current_user or store.current_user)


def search_stations(store, **kwargs):
    """Delegate search to the service."""
    return StationService(store).search(**kwargs)
