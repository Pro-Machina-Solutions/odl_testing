"""Shared fixtures for the odl_testing test suite."""

from collections.abc import Callable
from typing import Any

import pytest

from odl_testing.config import Config
from odl_testing.jobs import Service
from odl_testing.locations import Depot, Location
from odl_testing.vehicles import Vehicle, VehicleAct, VehicleType


@pytest.fixture
def location() -> Location:
    """A location whose coordinates need rounding when serialized."""
    return Location(name="TateModern", lat=51.507412345, lon=-0.100112345)


@pytest.fixture
def depot() -> Depot:
    return Depot(name="depot", lat=51.5416, lon=-0.1462)


@pytest.fixture
def make_config() -> Callable[..., Config]:
    """Build a Config with credentials, so no warning is raised."""

    def _make(**overrides: Any) -> Config:
        kwargs: dict[str, Any] = {"username": "user", "password": "secret"}
        kwargs.update(overrides)
        return Config(**kwargs)

    return _make


@pytest.fixture
def config(make_config: Callable[..., Config]) -> Config:
    return make_config()


@pytest.fixture
def make_service() -> Callable[..., Service]:
    def _make(name: str = "job-1", **overrides: Any) -> Service:
        kwargs: dict[str, Any] = {
            "name": name,
            "location": Location(name, 51.5074, -0.1001),
            "duration": 60_000,
            "open_time": "2099-01-01T09:00",
            "close_time": "2099-01-01T17:00",
        }
        kwargs.update(overrides)
        return Service(**kwargs)

    return _make


@pytest.fixture
def make_vehicle() -> Callable[..., Vehicle]:
    """Build a Vehicle; locations are omitted unless supplied."""

    def _make(**overrides: Any) -> Vehicle:
        kwargs: dict[str, Any] = {
            "name": "van-1",
            "start_time": "2026-08-07 09:00:00",
            "start_type": VehicleAct.START_AT_DEPOT,
            "late_time": "2026-08-07 17:30:00",
            "end_time": "2026-08-07 18:00:00",
            "end_type": VehicleAct.END_AT_DEPOT,
            "vtype": VehicleType(),
        }
        kwargs.update(overrides)
        return Vehicle(**kwargs)

    return _make
