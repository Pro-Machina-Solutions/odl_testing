from enum import StrEnum
from typing import Any

from .locations import Location


class JobType(StrEnum):
    SERVICE = "SERVICE"
    PICKUP = "PICKUP"
    DELIVER = "DELIVER"
    SHIPMENT_PICKUP = "SHIPMENT_PICKUP"
    SHIPMENT_DELIVERY = "SHIPMENT_DELIVERY"


class _Job:
    def __init__(
        self,
        name: str,
        location: Location,
        duration: int,  # in milliseconds
        open_time: str | None = None,
        late_time: str | None = None,
        close_time: str | None = None,
        _job_type: JobType | None = None,
    ):
        self.name = name
        self.location = location
        self.duration = duration
        self.open_time = open_time
        self.late_time = late_time
        self.close_time = close_time
        self._job_type = _job_type

    def _serialize(self) -> dict[str, Any]:
        rtn = {
            "_id": self.name,
            "type": self._job_type.value,
            "durationMillis": self.duration,
            "coordinate": self.location._serialize(),
        }
        # TODO Can an open time be specified without a close time?
        # Don't need a late time
        # Not sure if needed close time. Based on vehicle
        if self.open_time is not None:
            rtn["openTime"] = self.open_time
        if self.close_time is not None:
            rtn["closeTime"] = self.close_time
        if self.late_time is not None:
            rtn["lateTime"] = self.late_time

        return rtn

    def __repr__(self):
        return (
            f"<{self._job_type.value}: Location: {self.location._serialize()}>"
        )


class Service(_Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = JobType.SERVICE


class Pickup(_Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = JobType.PICKUP


class Delivery(_Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = JobType.DELIVER


class Shipment:
    # TODO
    pass
