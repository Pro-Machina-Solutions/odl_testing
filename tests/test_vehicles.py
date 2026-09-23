import pytest

from odl_testing.locations import Depot, Location
from odl_testing.vehicles import Vehicle, VehicleAct, VehicleType

DEFAULT_COSTS = {
    "costPerTravelHour": 1.0,
    "costPerWaitingHour": 0.5,
    "costPerServicingHour": 1.0,
    "costPerKm": 1.0e-6,
    "costFixed": 100.0,
    "costPerStop": 0.0,
}


class TestVehicleAct:
    def test_values(self):
        assert VehicleAct.START_AT_DEPOT.value == "START_AT_DEPOT"
        assert VehicleAct.END_AT_DEPOT.value == "RETURN_TO_DEPOT"

    def test_members_compare_equal_to_strings(self):
        assert VehicleAct.END_AT_DEPOT == "RETURN_TO_DEPOT"

    def test_lookup_by_value(self):
        assert VehicleAct("RETURN_TO_DEPOT") is VehicleAct.END_AT_DEPOT


class TestVehicleType:
    def test_defaults(self):
        vtype = VehicleType()
        assert vtype.cost_per_travel_hour == 1.0
        assert vtype.cost_per_wait_hour == 0.5
        assert vtype.cost_per_km == 1.0e-6
        assert vtype.cost_per_servicing_hour == 1.0
        assert vtype.fixed_cost == 100.0
        assert vtype.cost_per_stop == 0.0

    def test_serialise_defaults(self):
        assert VehicleType()._serialise() == DEFAULT_COSTS

    @pytest.mark.parametrize(
        ("argument", "key"),
        [
            ("cost_per_travel_hour", "costPerTravelHour"),
            ("cost_per_wait_hour", "costPerWaitingHour"),
            ("cost_per_km", "costPerKm"),
            ("cost_per_servicing_hour", "costPerServicingHour"),
            ("fixed_cost", "costFixed"),
            ("cost_per_stop", "costPerStop"),
        ],
    )
    def test_serialise_maps_each_argument_to_its_key(self, argument, key):
        serialised = VehicleType(**{argument: 42.0})._serialise()
        assert serialised == DEFAULT_COSTS | {key: 42.0}

    def test_serialise_returns_new_dict_each_call(self):
        vtype = VehicleType()
        vtype._serialise()["costFixed"] = -1
        assert vtype._serialise()["costFixed"] == 100.0


class TestVehicle:
    def test_attributes_are_stored(self, make_vehicle, depot):
        vtype = VehicleType()
        vehicle = make_vehicle(
            vtype=vtype, start_location=depot, end_location=depot
        )
        assert vehicle.name == "van-1"
        assert vehicle.start_time == "2026-08-07 09:00:00"
        assert vehicle.start_type is VehicleAct.START_AT_DEPOT
        assert vehicle.late_time == "2026-08-07 17:30:00"
        assert vehicle.end_time == "2026-08-07 18:00:00"
        assert vehicle.end_type is VehicleAct.END_AT_DEPOT
        assert vehicle.vtype is vtype
        assert vehicle.start_location is depot
        assert vehicle.end_location is depot

    def test_locations_default_to_none(self, make_vehicle):
        vehicle = make_vehicle()
        assert vehicle.start_location is None
        assert vehicle.end_location is None

    def test_serialise_without_locations(self, make_vehicle):
        assert make_vehicle()._serialise() == {
            "_id": "van-1",
            "definition": {
                "start": {
                    "type": "START_AT_DEPOT",
                    "openTime": "2026-08-07T09:00:00",
                },
                "end": {
                    "type": "RETURN_TO_DEPOT",
                    "lateTime": "2026-08-07T17:30:00",
                    "closeTime": "2026-08-07T18:00:00",
                },
                **DEFAULT_COSTS,
            },
        }

    def test_serialise_with_start_and_end_locations(self, make_vehicle):
        definition = make_vehicle(
            start_location=Depot("start", 51.54161234, -0.14621234),
            end_location=Location("end", 51.50741234, -0.10011234),
        )._serialise()["definition"]
        assert definition["start"]["coordinate"] == {
            "latitude": 51.5416,
            "longitude": -0.1462,
        }
        assert definition["end"]["coordinate"] == {
            "latitude": 51.5074,
            "longitude": -0.1001,
        }

    @pytest.mark.parametrize(
        ("given", "with_coord", "without_coord"),
        [
            ("start_location", "start", "end"),
            ("end_location", "end", "start"),
        ],
    )
    def test_serialise_with_one_location(
        self, make_vehicle, depot, given, with_coord, without_coord
    ):
        definition = make_vehicle(**{given: depot})._serialise()["definition"]
        assert "coordinate" in definition[with_coord]
        assert "coordinate" not in definition[without_coord]

    def test_serialise_uses_vehicle_type_costs(self, make_vehicle):
        vtype = VehicleType(fixed_cost=250.0, cost_per_stop=3.0)
        definition = make_vehicle(vtype=vtype)._serialise()["definition"]
        assert definition["costFixed"] == 250.0
        assert definition["costPerStop"] == 3.0

    def test_shared_vehicle_type_is_not_mutated(self, make_vehicle):
        vtype = VehicleType()
        before = vtype._serialise()
        make_vehicle(name="a", vtype=vtype)._serialise()
        make_vehicle(name="b", vtype=vtype)._serialise()
        assert vtype._serialise() == before

    def test_serialise_normalises_times(self, make_vehicle):
        definition = make_vehicle(
            start_time="2099-01-01T08:00",
            late_time="2099-01-01T18:00",
            end_time="2099-01-02T18:00",
        )._serialise()["definition"]
        assert definition["start"]["openTime"] == "2099-01-01T08:00:00"
        assert definition["end"]["lateTime"] == "2099-01-01T18:00:00"
        assert definition["end"]["closeTime"] == "2099-01-02T18:00:00"

    def test_serialise_uses_given_act_types(self, make_vehicle):
        definition = make_vehicle(
            start_type=VehicleAct.END_AT_DEPOT,
            end_type=VehicleAct.START_AT_DEPOT,
        )._serialise()["definition"]
        assert definition["start"]["type"] == "RETURN_TO_DEPOT"
        assert definition["end"]["type"] == "START_AT_DEPOT"

    @pytest.mark.parametrize("field", ["start_time", "late_time", "end_time"])
    def test_invalid_times_raise_value_error(self, make_vehicle, field):
        with pytest.raises(ValueError):
            make_vehicle(**{field: "not a time"})._serialise()

    def test_missing_required_arguments_raise_type_error(self):
        with pytest.raises(TypeError):
            Vehicle(name="v", start_time="2026-08-07")  # type: ignore[call-arg]
