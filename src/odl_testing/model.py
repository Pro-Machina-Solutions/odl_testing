from typing import Any

from .config import Config
from .jobs import _Job
from .vehicles import Vehicle
import json


class Model:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config if config is not None else Config()
        self.jobs: list[dict[str, Any]] = []
        self.vehicles: list[dict[str, Any]] = []
        self.base_json: dict[str, Any] = {
            "data": {
                "jobs": self.jobs,
                "vehicles": self.vehicles,
            },
            "configuration": self.config._serialize(),
        }

    def add_job(self, job: _Job) -> None:
        if not isinstance(job, _Job):
            raise TypeError("Incorrect job type")
        self.jobs.append(job._serialize())

    def add_vehicle(self, vehicle) -> None:
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Incorrect vehicle type")
        self.vehicles.append(vehicle._serialise())

    def build(self):
        print(json.dumps(self.base_json, indent=4))
