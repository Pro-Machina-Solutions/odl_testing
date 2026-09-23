import re
from unittest import mock

import pytest

from odl_testing.jobs import Delivery, Pickup, Service, Shipment
from odl_testing.locations import Depot, Location
from odl_testing.model import Model
from odl_testing.vehicles import VehicleAct, VehicleType


@pytest.fixture
def mock_client():
    """Replace the HTTP client used by Model with an autospecced mock.

    ``client.py`` is out of scope for these tests, so ``Model`` is tested in
    isolation from it.
    """
    with mock.patch("odl_testing.model.Client", autospec=True) as client_cls:
        yield client_cls


@pytest.fixture
def model(mock_client, config) -> Model:
    return Model(config)


@pytest.fixture
def depot_vehicle(make_vehicle, depot):
    def _make(name: str = "van-1"):
        return make_vehicle(
            name=name,
            start_time="2099-01-01T08:00",
            late_time="2099-01-01T18:00",
            end_time="2099-01-02T18:00",
            start_location=depot,
            end_location=depot,
        )

    return _make


class TestModelInit:
    def test_uses_supplied_config(self, model, config):
        assert model.config is config

    def test_creates_default_config_when_none_supplied(self, mock_client):
        with mock.patch("odl_testing.model.Config") as config_cls:
            config_cls.return_value._serialize.return_value = {"d": 1}
            model = Model()
        config_cls.assert_called_once_with()
        assert model.config is config_cls.return_value
        assert model.build()["configuration"] == {"d": 1}

    def test_starts_with_no_jobs_or_vehicles(self, model):
        assert model.jobs == []
        assert model.vehicles == []

    def test_initial_payload_structure(self, mock_client, make_config):
        cfg = make_config(use_road_network=True)
        assert Model(cfg).build() == {
            "data": {"jobs": [], "vehicles": []},
            "configuration": cfg._serialize(),
        }

    def test_creates_a_client_with_the_model_config(
        self, model, mock_client, config
    ):
        mock_client.assert_called_once_with(config=config)
        assert model.client is mock_client.return_value

    def test_client_gets_default_config_when_none_supplied(self, mock_client):
        with mock.patch("odl_testing.model.Config") as config_cls:
            config_cls.return_value._serialize.return_value = {}
            Model()
        mock_client.assert_called_once_with(config=config_cls.return_value)

    def test_model_id_is_32_char_hex(self, model):
        assert re.fullmatch(r"[0-9a-f]{32}", model.model_id)

    def test_model_ids_are_unique(self, mock_client, config):
        assert len({Model(config).model_id for _ in range(50)}) == 50

    def test_models_do_not_share_state(
        self, mock_client, config, make_service
    ):
        first, second = Model(config), Model(config)
        first.add_job(make_service())
        assert second.jobs == []
        assert second.build()["data"]["jobs"] == []


class TestAddJob:
    def test_appends_serialized_job(self, model, make_service):
        job = make_service()
        model.add_job(job)
        assert model.jobs == [job._serialize()]

    def test_accepts_every_job_subclass(self, model, location):
        for job in (
            Service("s", location, 1),
            Pickup("p", location, 1),
            Delivery("d", location, 1),
        ):
            model.add_job(job)
        assert [j["_id"] for j in model.jobs] == ["s", "p", "d"]

    def test_preserves_insertion_order(self, model, make_service):
        for name in ("c", "a", "b"):
            model.add_job(make_service(name))
        assert [j["_id"] for j in model.jobs] == ["c", "a", "b"]

    def test_added_jobs_appear_in_built_payload(self, model, make_service):
        model.add_job(make_service())
        assert model.build()["data"]["jobs"] == model.jobs

    def test_job_is_snapshotted_when_added(self, model, make_service):
        job = make_service()
        model.add_job(job)
        job.name = "renamed"
        assert model.jobs[0]["_id"] == "job-1"

    @pytest.mark.parametrize(
        "bad",
        [
            None,
            "job",
            {"_id": "job"},
            Location("x", 1.0, 2.0),
            VehicleAct.START_AT_DEPOT,
            Shipment(),
        ],
        ids=repr,
    )
    def test_rejects_non_jobs(self, model, bad):
        with pytest.raises(TypeError, match="Incorrect job type"):
            model.add_job(bad)
        assert model.jobs == []

    def test_rejects_vehicle(self, model, depot_vehicle):
        with pytest.raises(TypeError, match="Incorrect job type"):
            model.add_job(depot_vehicle())


class TestAddVehicle:
    def test_appends_serialised_vehicle(self, model, depot_vehicle):
        vehicle = depot_vehicle()
        model.add_vehicle(vehicle)
        assert model.vehicles == [vehicle._serialise()]

    def test_added_vehicles_appear_in_built_payload(
        self, model, depot_vehicle
    ):
        model.add_vehicle(depot_vehicle("a"))
        model.add_vehicle(depot_vehicle("b"))
        ids = [v["_id"] for v in model.build()["data"]["vehicles"]]
        assert ids == ["a", "b"]

    @pytest.mark.parametrize(
        "bad", [None, "van", VehicleType(), Depot("d", 1.0, 2.0)], ids=repr
    )
    def test_rejects_non_vehicles(self, model, bad):
        with pytest.raises(TypeError, match="Incorrect vehicle type"):
            model.add_vehicle(bad)
        assert model.vehicles == []

    def test_rejects_job(self, model, make_service):
        with pytest.raises(TypeError, match="Incorrect vehicle type"):
            model.add_vehicle(make_service())


class TestBuildAndSend:
    def test_build_returns_base_payload(self, model):
        assert model.build() is model._base_json

    def test_build_reflects_items_added_after_previous_build(
        self, model, make_service
    ):
        payload = model.build()
        model.add_job(make_service())
        assert len(payload["data"]["jobs"]) == 1

    @pytest.mark.parametrize("offline", [True, False])
    def test_send_returns_payload_whatever_the_offline_flag(
        self, model, offline
    ):
        model.config._offline = offline
        assert model.send() is model._base_json

    def test_send_does_not_call_the_client_yet(self, model):
        model.send()
        assert model.client.mock_calls == []


class TestFullPayload:
    """End-to-end check of the payload built from all the model pieces."""

    def test_full_payload(self, model, make_service, depot_vehicle):
        model.add_job(make_service("TateModern1"))
        model.add_vehicle(depot_vehicle("vehicle1"))
        depot_coordinate = {"latitude": 51.5416, "longitude": -0.1462}

        assert model.build() == {
            "data": {
                "jobs": [
                    {
                        "_id": "TateModern1",
                        "stops": [
                            {
                                "type": "SERVICE",
                                "durationMillis": 60_000,
                                "coordinate": {
                                    "latitude": 51.5074,
                                    "longitude": -0.1001,
                                },
                                "openTime": "2099-01-01T09:00:00",
                                "closeTime": "2099-01-01T17:00:00",
                                "lateTime": "2099-01-01T17:00:00",
                            }
                        ],
                    }
                ],
                "vehicles": [
                    {
                        "_id": "vehicle1",
                        "definition": {
                            "start": {
                                "type": "START_AT_DEPOT",
                                "openTime": "2099-01-01T08:00:00",
                                "coordinate": depot_coordinate,
                            },
                            "end": {
                                "type": "RETURN_TO_DEPOT",
                                "lateTime": "2099-01-01T18:00:00",
                                "closeTime": "2099-01-02T18:00:00",
                                "coordinate": depot_coordinate,
                            },
                            "costPerTravelHour": 1.0,
                            "costPerWaitingHour": 0.5,
                            "costPerServicingHour": 1.0,
                            "costPerKm": 1.0e-6,
                            "costFixed": 100.0,
                            "costPerStop": 0.0,
                        },
                    }
                ],
            },
            "configuration": {
                "distances": {
                    "roadNetworkTimeMultiplier": 1.0,
                    "useRoadNetwork": False,
                    "straightLineSpeedMetresPerSec": 22.352,
                    "straightLineDistanceMultiplier": 1.0,
                }
            },
        }

    def test_payload_contains_no_credentials(
        self, mock_client, make_config, make_service, depot_vehicle
    ):
        model = Model(make_config(username="u-XYZ", password="p-ABC"))
        model.add_job(make_service())
        model.add_vehicle(depot_vehicle())
        assert not re.search("u-XYZ|p-ABC", repr(model.build()))
