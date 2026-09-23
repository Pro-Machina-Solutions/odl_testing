import pytest

from odl_testing.jobs import (
    Delivery,
    Pickup,
    Service,
    Shipment,
    _Job,
    _JobType,
)

JOB_CLASSES = [
    pytest.param(Service, _JobType.SERVICE, id="Service"),
    pytest.param(Pickup, _JobType.PICKUP, id="Pickup"),
    pytest.param(Delivery, _JobType.DELIVER, id="Delivery"),
]


def first_stop(job: _Job) -> dict:
    return job._serialize()["stops"][0]


class TestJobType:
    def test_values(self):
        assert {m.name: m.value for m in _JobType} == {
            "SERVICE": "SERVICE",
            "PICKUP": "PICKUP",
            "DELIVER": "DELIVER",
            "SHIPMENT_PICKUP": "SHIPMENT_PICKUP",
            "SHIPMENT_DELIVERY": "SHIPMENT_DELIVERY",
        }

    def test_members_compare_equal_to_strings(self):
        assert _JobType.SERVICE == "SERVICE"
        assert str(_JobType.DELIVER) == "DELIVER"


class TestJobConstruction:
    @pytest.mark.parametrize(("cls", "expected"), JOB_CLASSES)
    def test_subclass_sets_its_job_type(self, cls, expected, location):
        job = cls(name="j", location=location, duration=1000)
        assert isinstance(job, _Job)
        assert job._job_type is expected

    def test_attributes_are_stored(self, location):
        job = Service(
            name="j",
            location=location,
            duration=60_000,
            open_time="2026-08-07 09:00",
            late_time="2026-08-07 10:00",
            close_time="2026-08-07 11:00",
        )
        assert job.name == "j"
        assert job.location is location
        assert job.duration == 60_000
        assert job.open_time == "2026-08-07 09:00"
        assert job.late_time == "2026-08-07 10:00"
        assert job.close_time == "2026-08-07 11:00"

    def test_time_windows_default_to_none(self, location):
        job = Pickup("j", location, 1000)
        assert job.open_time is None
        assert job.late_time is None
        assert job.close_time is None

    def test_positional_arguments(self, location):
        job = Delivery(
            "j", location, 5, "2026-01-01", "2026-01-02", "2026-01-03"
        )
        assert (job.open_time, job.late_time, job.close_time) == (
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        )

    def test_caller_cannot_override_subclass_job_type(self, location):
        job = Service("j", location, 1, _job_type=_JobType.PICKUP)
        assert job._job_type is _JobType.SERVICE

    @pytest.mark.parametrize(("cls", "_expected"), JOB_CLASSES)
    def test_missing_required_arguments(self, cls, _expected, location):
        with pytest.raises(TypeError):
            cls(name="j", location=location)

    def test_base_job_has_no_type_by_default(self, location):
        assert _Job("j", location, 1)._job_type is None


class TestJobSerialize:
    def test_top_level_structure(self, location):
        out = Service("job-1", location, 1000)._serialize()
        assert set(out) == {"_id", "stops"}
        assert out["_id"] == "job-1"
        assert isinstance(out["stops"], list)
        assert len(out["stops"]) == 1

    @pytest.mark.parametrize("key", ["openTime", "lateTime", "closeTime"])
    def test_no_time_keys_when_times_omitted(self, key, location):
        assert key not in first_stop(Service("j", location, 1000))

    def test_open_time_only(self, location):
        stop = first_stop(
            Service("j", location, 1000, open_time="2026-08-07 09:00")
        )
        assert stop.get("openTime") == "2026-08-07T09:00:00"
        assert "closeTime" not in stop
        assert "lateTime" not in stop

    def test_late_time_defaults_to_close_time(self, location):
        stop = first_stop(
            Service(
                "j",
                location,
                1000,
                open_time="2026-08-07 09:00",
                close_time="2026-08-07 11:00",
            )
        )
        assert stop["openTime"] == "2026-08-07T09:00:00"
        assert stop["closeTime"] == "2026-08-07T11:00:00"
        assert stop["lateTime"] == "2026-08-07T11:00:00"

    def test_explicit_late_time_is_used(self, location):
        stop = first_stop(
            Service(
                "j",
                location,
                1000,
                late_time="2026-08-07 10:00",
                close_time="2026-08-07 11:00",
            )
        )
        assert stop["lateTime"] == "2026-08-07T10:00:00"
        assert stop["closeTime"] == "2026-08-07T11:00:00"

    def test_late_time_without_close_time(self, location):
        stop = first_stop(
            Service("j", location, 1000, late_time="2026-08-07 10:00")
        )
        assert stop["lateTime"] == "2026-08-07T10:00:00"
        assert "closeTime" not in stop

    def test_times_are_normalised_to_iso_format(self, location):
        stop = first_stop(
            Service(
                "j",
                location,
                1000,
                open_time="2099-01-01T09:00",
                late_time="2099-01-01T17:00",
                close_time="2099-01-02T17:00",
            )
        )
        assert stop["openTime"] == "2099-01-01T09:00:00"
        assert stop["lateTime"] == "2099-01-01T17:00:00"
        assert stop["closeTime"] == "2099-01-02T17:00:00"

    @pytest.mark.parametrize("field", ["open_time", "late_time", "close_time"])
    def test_invalid_time_raises_value_error(self, field, location):
        job = Service("j", location, 1000, **{field: "whenever"})
        with pytest.raises(ValueError):
            job._serialize()

    def test_serialize_returns_a_new_dict_each_call(self, location):
        job = Service("j", location, 1000)
        first_stop(job)["openTime"] = "tampered"
        assert "openTime" not in first_stop(job)

    def test_base_job_without_type_cannot_be_serialized(self, location):
        with pytest.raises(AssertionError):
            _Job("j", location, 1000)._serialize()

    @pytest.mark.parametrize(("cls", "expected"), JOB_CLASSES)
    def test_stop_includes_job_type(self, cls, expected, location):
        assert first_stop(cls("j", location, 1000))["type"] == expected.value

    def test_stop_includes_duration_in_millis(self, location):
        stop = first_stop(Service("j", location, 3_600_000))
        assert stop["durationMillis"] == 3_600_000

    def test_stop_includes_rounded_coordinate(self, location):
        assert first_stop(Service("j", location, 1000))["coordinate"] == {
            "latitude": 51.5074,
            "longitude": -0.1001,
        }

    def test_full_stop_without_time_window(self, location):
        assert first_stop(Pickup("j", location, 1000)) == {
            "type": "PICKUP",
            "durationMillis": 1000,
            "coordinate": {"latitude": 51.5074, "longitude": -0.1001},
        }

    def test_full_stop_with_time_window(self, location):
        assert first_stop(
            Delivery(
                "j",
                location,
                3_600_000,
                open_time="2099-01-01T09:00",
                late_time="2099-01-01T17:00",
                close_time="2099-01-02T17:00",
            )
        ) == {
            "type": "DELIVER",
            "durationMillis": 3_600_000,
            "coordinate": {"latitude": 51.5074, "longitude": -0.1001},
            "openTime": "2099-01-01T09:00:00",
            "lateTime": "2099-01-01T17:00:00",
            "closeTime": "2099-01-02T17:00:00",
        }

    def test_coordinate_reflects_location_at_serialize_time(self, location):
        job = Service("j", location, 1000)
        location.lat = 12.34567
        assert first_stop(job)["coordinate"]["latitude"] == 12.3457


class TestJobRepr:
    def test_repr_includes_type_and_serialized_location(self, location):
        coordinate = {"latitude": 51.5074, "longitude": -0.1001}
        assert (
            repr(Service("j", location, 1000))
            == f"<SERVICE: Location: {coordinate}>"
        )

    @pytest.mark.parametrize(("cls", "expected"), JOB_CLASSES)
    def test_repr_for_each_subclass(self, cls, expected, location):
        assert repr(cls("j", location, 1)).startswith(
            f"<{expected.value}: Location: "
        )

    def test_repr_of_untyped_base_job_raises(self, location):
        with pytest.raises(AttributeError):
            repr(_Job("j", location, 1))


class TestShipment:
    """Shipment is still a TODO placeholder."""

    def test_can_be_instantiated(self):
        assert isinstance(Shipment(), Shipment)

    def test_is_not_yet_a_job(self):
        assert not issubclass(Shipment, _Job)
