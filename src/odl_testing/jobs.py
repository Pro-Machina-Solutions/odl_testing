import datetime as dt
from enum import StrEnum
from typing import Any

from .locations import Location


class _JobType(StrEnum):
    SERVICE = "SERVICE"
    PICKUP = "PICKUP"
    DELIVER = "DELIVER"
    SHIPMENT_PICKUP = "SHIPMENT_PICKUP"
    SHIPMENT_DELIVERY = "SHIPMENT_DELIVERY"


class _Job:
    """Base class for pickups, deliveries and services"""

    def __init__(
        self,
        name: str,
        location: Location,
        duration: int,  # in milliseconds
        open_time: str | None = None,
        late_time: str | None = None,
        close_time: str | None = None,
        _job_type: _JobType | None = None,
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
            "stops": [
                {
                    "type": self._job_type.value,
                    "durationMillis": self.duration,
                    "coordinate": self.location._serialize(),
                }
            ],
        }
        # TODO Can an open time be specified without a close time?
        # Don't need a late time
        # Not sure if needed close time. Based on vehicle
        if self.open_time is not None:
            rtn["stops"][0]["openTime"] = dt.datetime.fromisoformat(
                self.open_time
            ).isoformat()
        if self.close_time is not None:
            rtn["stops"][0]["closeTime"] = dt.datetime.fromisoformat(
                self.close_time
            ).isoformat()
        if self.late_time is not None:
            rtn["stops"][0]["lateTime"] = dt.datetime.fromisoformat(
                self.late_time
            ).isoformat()
        else:
            rtn["stops"][0]["lateTime"] = dt.datetime.fromisoformat(
                self.close_time
            ).isoformat()

        return rtn

    def __repr__(self):
        return (
            f"<{self._job_type.value}: Location: {self.location._serialize()}>"
        )


class Service(_Job):
    """Create a job that has no capacity constraints

    Parameters
    ----------
    name : str
        A string identifier for the Service
    location : Location
        A Location object specifying the lat/long of the job
    duration : int
        The length of time the Service takes, in milliseconds
    late_time : str | None, optional
        The time after which an arrival will cause a cost penalty
    close_time : str | None, optional
        The latest time that an arrival can occur
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = _JobType.SERVICE


class Pickup(_Job):
    """Create a job that has no capacity constraints

    Parameters
    ----------
    name : str
        A string identifier for the Pickup
    location : Location
        A Location object specifying the lat/long of the job
    duration : int
        The length of time the Pickup takes, in milliseconds
    late_time : str | None, optional
        The time after which an arrival will cause a cost penalty
    close_time : str | None, optional
        The latest time that an arrival can occur
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = _JobType.PICKUP


class Delivery(_Job):
    """Create a job that has no capacity constraints

    Parameters
    ----------
    name : str
        A string identifier for the Pickup
    location : Location
        A Location object specifying the lat/long of the job
    duration : int
        The length of time the Pickup takes, in milliseconds
    late_time : str | None, optional
        The time after which an arrival will cause a cost penalty
    close_time : str | None, optional
        The latest time that an arrival can occur
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_type = _JobType.DELIVER


class Shipment:
    # TODO
    pass
