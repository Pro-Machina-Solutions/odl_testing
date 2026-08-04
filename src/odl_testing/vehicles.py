from enum import StrEnum
from typing import Any

from .locations import Location


class VehicleAct(StrEnum):
    START_AT_DEPOT = "START_AT_DEPOT"
    END_AT_DEPOT = "END_AT_DEPOT"


class VehicleType:
    def __init__(
        self,
        cost_per_travel_hour: float = 1.0,
        cost_per_wait_hour: float = 0.5,
        cost_per_km: float = 1.0e-6,
        cost_per_servicing_hour: float = 1.0,
        fixed_cost: float = 100.0,
        cost_per_stop: float = 0.0,
    ) -> None:
        self.cost_per_travel_hour = cost_per_travel_hour
        self.cost_per_wait_hour = cost_per_wait_hour
        self.cost_per_km = cost_per_km
        self.cost_per_servicing_hour = cost_per_servicing_hour
        self.fixed_cost = fixed_cost
        self.cost_per_stop = cost_per_stop

    def _serialise(self) -> dict:
        return {
            "costPerTravelHour": self.cost_per_travel_hour,
            "costPerWaitingHour": self.cost_per_wait_hour,
            "costPerServicingHour": self.cost_per_servicing_hour,
            "costPerKm": self.cost_per_km,
            "costFixed": self.fixed_cost,
            "costPerStop": self.cost_per_stop,
        }


class Vehicle:
    def __init__(
        self,
        name: str,
        start_time: str,
        start_type: VehicleAct,
        late_time: str,
        end_time: str,
        end_type: VehicleAct,
        vtype: VehicleType,
        start_location: Location | None = None,
        end_location: Location | None = None,
    ):
        self.name = name
        self.start_time = start_time
        self.start_type = start_type
        self.late_time = late_time
        self.end_time = end_time
        self.end_type = end_type
        self.vtype = vtype
        self.start_location = start_location
        self.end_location = end_location

    def _serialise(self) -> dict:
        inner: dict[str, Any] = {}
        start: dict[str, Any] = {
            "type": self.start_type.value,
            "openTime": self.start_time,
        }
        if self.start_location is not None:
            start["coordinate"] = (self.start_location._serialize(),)

        end: dict[Any, Any] = {
            "type": self.end_type.value,
            "lateTime": self.late_time,
            "closeTime": self.end_time,
        }
        if self.end_location is not None:
            end["coordinate"] = self.end_location._serialize()

        inner = {
            "start": start,
            "end": end,
        }
        inner = inner | self.vtype._serialise()
        return {
            "definition": inner,
            "_id": self.name,
        }
