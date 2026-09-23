import pytest

from odl_testing.locations import Depot, Location


class TestLocation:
    def test_attributes_are_stored(self):
        loc = Location(name="home", lat=51.5074, lon=-0.1278)
        assert (loc.name, loc.lat, loc.lon) == ("home", 51.5074, -0.1278)

    def test_positional_arguments(self):
        loc = Location("home", 1.0, 2.0)
        assert (loc.name, loc.lat, loc.lon) == ("home", 1.0, 2.0)

    def test_serialize_keys(self):
        assert Location("a", 1.0, 2.0)._serialize() == {
            "latitude": 1.0,
            "longitude": 2.0,
        }

    def test_serialize_rounds_to_four_decimal_places(self, location):
        assert location._serialize() == {
            "latitude": 51.5074,
            "longitude": -0.1001,
        }

    def test_serialize_does_not_mutate_stored_coordinates(self, location):
        location._serialize()
        assert location.lat == 51.507412345
        assert location.lon == -0.100112345

    def test_serialize_accepts_integers(self):
        assert Location("a", 10, -20)._serialize() == {
            "latitude": 10,
            "longitude": -20,
        }

    def test_serialize_does_not_include_name(self, location):
        assert "name" not in location._serialize()

    def test_serialize_returns_new_dict_each_call(self):
        loc = Location("a", 1.0, 2.0)
        loc._serialize()["latitude"] = 99
        assert loc._serialize()["latitude"] == 1.0

    def test_repr_uses_six_decimal_places(self):
        assert (
            repr(Location("shop", 12.5, -70.0123456789))
            == "<Location: shop. Latitude: 12.500000, Longitude: -70.012346>"
        )

    def test_missing_argument_raises_type_error(self):
        with pytest.raises(TypeError):
            Location("a", 1.0)  # type: ignore[call-arg]


class TestDepot:
    def test_is_a_location(self, depot):
        assert isinstance(depot, Location)

    def test_keyword_arguments(self):
        depot = Depot(name="d", lat=1.0, lon=2.0)
        assert (depot.name, depot.lat, depot.lon) == ("d", 1.0, 2.0)

    def test_serializes_like_a_location(self):
        args = ("d", 51.54161234, -0.14621234)
        assert Depot(*args)._serialize() == Location(*args)._serialize()

    def test_repr_identifies_as_depot(self):
        assert (
            repr(Depot("hub", 51.5416, -0.1462))
            == "<Depot: hub. Latitude: 51.541600, Longitude: -0.146200>"
        )

    def test_missing_argument_raises_type_error(self):
        with pytest.raises(TypeError):
            Depot("hub", 51.5)  # type: ignore[call-arg]
