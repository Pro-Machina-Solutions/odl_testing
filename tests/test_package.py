import pytest

import odl_testing
from odl_testing import jobs, locations, model, vehicles


@pytest.mark.parametrize(
    ("name", "obj"),
    [
        ("Delivery", jobs.Delivery),
        ("Pickup", jobs.Pickup),
        ("Service", jobs.Service),
        ("Shipment", jobs.Shipment),
        ("Depot", locations.Depot),
        ("Location", locations.Location),
        ("Model", model.Model),
        ("Vehicle", vehicles.Vehicle),
        ("VehicleAct", vehicles.VehicleAct),
        ("VehicleType", vehicles.VehicleType),
    ],
)
def test_public_name_is_exported(name, obj):
    assert getattr(odl_testing, name) is obj


@pytest.mark.parametrize("name", ["_Job", "_JobType"])
def test_private_job_classes_are_not_exported(name):
    assert not hasattr(odl_testing, name)
