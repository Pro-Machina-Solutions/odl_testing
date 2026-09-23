import uuid
from typing import Any

from .client import Client
from .config import Config
from .jobs import _Job
from .vehicles import Vehicle


class Model:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config if config is not None else Config()
        self.jobs: list[dict[str, Any]] = []
        self.vehicles: list[dict[str, Any]] = []
        self._base_json: dict[str, Any] = {
            "data": {
                "jobs": self.jobs,
                "vehicles": self.vehicles,
            },
            "configuration": self.config._serialize(),
        }
        self.client = Client()
        self.model_id = uuid.uuid4().hex

    def add_job(self, job: _Job) -> None:
        if not isinstance(job, _Job):
            raise TypeError("Incorrect job type")
        self.jobs.append(job._serialize())

    def add_vehicle(self, vehicle) -> None:
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Incorrect vehicle type")
        self.vehicles.append(vehicle._serialise())

    def build(self) -> dict[str, Any]:
        # TODO for now we just send the same JSON object back, but we might
        # need to add other modifications required in future
        return self._base_json

    def send(self) -> dict[str, Any]:
        if self.config._offline:
            return self._base_json
        return self._base_json
