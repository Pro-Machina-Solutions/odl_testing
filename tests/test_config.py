import importlib.util
import warnings
from types import ModuleType
from unittest import mock

import pytest

from odl_testing import config as config_module
from odl_testing.config import Config

NO_CREDENTIALS_MESSAGE = (
    "No login credentials supplied, so problem can only be built but not"
    " dispatched to be solved"
)


@pytest.fixture
def load_fresh_config(monkeypatch):
    """Execute config.py as a brand new module in a controlled environment.

    ``Config``'s default username/password are read from the environment when
    the module is imported, and the import also loads any ``.env`` file. To
    test that without touching a real ``.env`` or the already imported
    ``odl_testing.config`` module, a separate copy of the module is executed
    with dotenv mocked out and only the given variables in the environment.
    """
    load_dotenv = mock.Mock(name="load_dotenv")
    find_dotenv = mock.Mock(name="find_dotenv", return_value="/x/.env")
    monkeypatch.setattr("dotenv.load_dotenv", load_dotenv)
    monkeypatch.setattr("dotenv.find_dotenv", find_dotenv)

    def _load(**env: str) -> ModuleType:
        for name in ("USER_NAME", "USER_PASS"):
            monkeypatch.delenv(name, raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        spec = importlib.util.spec_from_file_location(
            "_fresh_odl_testing_config", config_module.__file__
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    _load.load_dotenv = load_dotenv  # type: ignore[attr-defined]
    _load.find_dotenv = find_dotenv  # type: ignore[attr-defined]
    return _load


class TestConfigDefaults:
    def test_default_connection_settings(self, config):
        assert config.base_url == "http://127.0.0.1"
        assert config.port == "8080"

    def test_default_distance_settings(self, config):
        assert config.road_network_time_multiplier == 1.0
        assert config.use_road_networks is False
        assert config.straight_line_speed_metres_per_sec == 22.352
        assert config.straight_line_distance_multiplier == 1.0

    def test_import_loads_dotenv_file(self, load_fresh_config):
        load_fresh_config()
        load_fresh_config.find_dotenv.assert_called_once_with()
        load_fresh_config.load_dotenv.assert_called_once_with("/x/.env")

    def test_credentials_default_to_environment_at_import_time(
        self, load_fresh_config
    ):
        module = load_fresh_config(USER_NAME="env-user", USER_PASS="env-pass")
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # no warning expected
            cfg = module.Config()
        assert cfg.username == "env-user"
        assert cfg.password == "env-pass"

    def test_credentials_default_to_none_without_environment(
        self, load_fresh_config
    ):
        module = load_fresh_config()
        with pytest.warns(UserWarning):
            cfg = module.Config()
        assert cfg.username is None
        assert cfg.password is None

    def test_environment_changes_after_import_do_not_affect_defaults(
        self, load_fresh_config, monkeypatch
    ):
        # Defaults are bound when the function is defined, not per call.
        module = load_fresh_config()
        monkeypatch.setenv("USER_NAME", "late")
        monkeypatch.setenv("USER_PASS", "late")
        with pytest.warns(UserWarning):
            cfg = module.Config()
        assert cfg.username is None


class TestConfigArguments:
    def test_custom_values_are_stored(self):
        cfg = Config(
            base_url="https://solver.example",
            port=9000,
            username="u",
            password="p",
            road_network_time_multiplier=1.2,
            use_road_network=True,
            straight_line_speed_metres_per_sec=10.0,
            straight_line_distance_multiplier=1.3,
        )
        assert cfg.base_url == "https://solver.example"
        assert cfg.port == "9000"
        assert cfg.username == "u"
        assert cfg.password == "p"
        assert cfg.road_network_time_multiplier == 1.2
        assert cfg.use_road_networks is True
        assert cfg.straight_line_speed_metres_per_sec == 10.0
        assert cfg.straight_line_distance_multiplier == 1.3

    @pytest.mark.parametrize(
        ("port", "expected"), [(443, "443"), ("8443", "8443")]
    )
    def test_port_is_stored_as_string(self, make_config, port, expected):
        assert make_config(port=port).port == expected


class TestConfigCredentials:
    def test_no_warning_when_credentials_supplied(self, make_config):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            make_config()

    @pytest.mark.parametrize(
        ("username", "password"),
        [
            pytest.param(None, None, id="both-missing"),
            pytest.param(None, "p", id="username-missing"),
            pytest.param("u", None, id="password-missing"),
        ],
    )
    def test_warns_when_credentials_missing(self, username, password):
        with pytest.warns(UserWarning, match=NO_CREDENTIALS_MESSAGE):
            Config(username=username, password=password)

    def test_empty_strings_count_as_supplied(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            Config(username="", password="")

    @pytest.mark.parametrize(
        ("username", "password"),
        [
            pytest.param(None, None, id="both-missing"),
            pytest.param(None, "p", id="username-missing"),
            pytest.param("u", None, id="password-missing"),
        ],
    )
    def test_offline_when_credentials_missing(self, username, password):
        with pytest.warns(UserWarning):
            cfg = Config(username=username, password=password)
        assert cfg._offline is True

    def test_online_when_credentials_supplied(self, config):
        assert config._offline is False


class TestConfigSerialize:
    def test_serialize_defaults(self, config):
        assert config._serialize() == {
            "distances": {
                "roadNetworkTimeMultiplier": 1.0,
                "useRoadNetwork": False,
                "straightLineSpeedMetresPerSec": 22.352,
                "straightLineDistanceMultiplier": 1.0,
            }
        }

    def test_serialize_custom_values(self, make_config):
        cfg = make_config(
            road_network_time_multiplier=1.5,
            use_road_network=True,
            straight_line_speed_metres_per_sec=13.4,
            straight_line_distance_multiplier=1.25,
        )
        assert cfg._serialize() == {
            "distances": {
                "roadNetworkTimeMultiplier": 1.5,
                "useRoadNetwork": True,
                "straightLineSpeedMetresPerSec": 13.4,
                "straightLineDistanceMultiplier": 1.25,
            }
        }

    @pytest.mark.parametrize("secret", ["user", "secret", "127.0.0.1", "8080"])
    def test_serialize_excludes_connection_details_and_credentials(
        self, config, secret
    ):
        assert secret not in repr(config._serialize())

    def test_serialize_reflects_attribute_changes(self, config):
        config.use_road_networks = True
        assert config._serialize()["distances"]["useRoadNetwork"] is True

    def test_serialize_returns_new_dict_each_call(self, config):
        assert config._serialize() is not config._serialize()
