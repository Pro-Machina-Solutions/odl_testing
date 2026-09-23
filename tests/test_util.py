import pytest

from odl_testing.util import convert_to_model_time


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        pytest.param(
            "2026-08-07 09:00:00", "2026-08-07T09:00:00", id="space-sep"
        ),
        pytest.param(
            "2026-08-07T09:00:00", "2026-08-07T09:00:00", id="already-iso"
        ),
        pytest.param(
            "2099-01-01T08:00", "2099-01-01T08:00:00", id="pads-seconds"
        ),
        pytest.param("2026-08-07", "2026-08-07T00:00:00", id="date-only"),
        pytest.param(
            "2026-08-07T09:00:00.123456",
            "2026-08-07T09:00:00.123456",
            id="microseconds",
        ),
        pytest.param(
            "20260807T090000", "2026-08-07T09:00:00", id="basic-format"
        ),
        # Timezone-aware inputs are passed through unchanged for now (see the
        # TODO in util.py about converting to UTC).
        pytest.param(
            "2026-08-07T09:00:00+01:00",
            "2026-08-07T09:00:00+01:00",
            id="tz-offset",
        ),
        pytest.param(
            "2026-08-07T09:00:00Z", "2026-08-07T09:00:00+00:00", id="zulu"
        ),
    ],
)
def test_converts_to_iso_format(timestamp, expected):
    assert convert_to_model_time(timestamp) == expected


def test_returns_str():
    assert isinstance(convert_to_model_time("2026-08-07"), str)


def test_is_idempotent():
    once = convert_to_model_time("2026-08-07 09:00")
    assert convert_to_model_time(once) == once


@pytest.mark.parametrize("bad", ["not a date", "", "2026-13-01", "2026-02-30"])
def test_invalid_string_raises_value_error(bad):
    with pytest.raises(ValueError):
        convert_to_model_time(bad)


@pytest.mark.parametrize("bad", [None, 20260807, 1.5])
def test_non_string_raises_type_error(bad):
    with pytest.raises(TypeError):
        convert_to_model_time(bad)
