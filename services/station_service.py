"""Backwards‑compatible wrappers around StationService class."""

from AnthonysCodeEdits.services.station_service import StationService


def create_voting_station(store, current_user=None):
    return StationService(store).create(current_user or store.current_user)


def view_all_stations(store):
    return StationService(store).view_all()


def update_station(store, current_user=None):
    return StationService(store).update(current_user or store.current_user)


def delete_station(store, current_user=None):
    return StationService(store).delete(current_user or store.current_user)


def search_stations(store, **kwargs):
    return StationService(store).search(**kwargs)
