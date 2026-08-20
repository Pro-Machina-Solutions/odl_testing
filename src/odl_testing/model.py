import json
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
        self.base_json: dict[str, Any] = {
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

    def build(self):
        with open("model_output.json", "w") as outfile:
            json.dump(self.base_json, outfile, indent=4)
        test_json = """
        {
            "data": {
                "jobs": [
                    {
                        "stops": [
                            {
                                "type": "SERVICE",
                                "coordinate": {
                                    "latitude": 51.5074,
                                    "longitude": -0.1001
                                },
                                "openTime": "2099-01-01T09:00",
                                "lateTime": "2099-01-01T17:00",
                                "closeTime": "2099-01-02T17:00",
                                "durationMillis": 3600000,
                                "_id": "TateModern1"
                            }
                        ],
                        "_id": "TateModern1"
                    }
                ],
                "vehicles": [
                    {
                        "definition": {
                            "start": {
                                "type": "START_AT_DEPOT",
                                "coordinate": {
                                    "latitude": 51.5416,
                                    "longitude": -0.1462
                                },
                                "openTime": "2099-01-01T08:00"
                            },
                            "end": {
                                "type": "RETURN_TO_DEPOT",
                                "coordinate": {
                                    "latitude": 51.5416,
                                    "longitude": -0.1462
                                },
                                "lateTime": "2099-01-01T18:00",
                                "closeTime": "2099-01-02T18:00"
                            },
                            "costPerTravelHour": 1.0,
                            "costPerWaitingHour": 0.5,
                            "costPerServicingHour": 1.0,
                            "costPerKm": 1e-06,
                            "costFixed": 100.0,
                            "costPerStop": 0.0
                        },
                        "_id": "Camden1"
                    }
                ]
            },
            "configuration": {
                "distances": {
                    "roadNetworkTimeMultiplier": 1.0,
                    "useRoadNetwork": false,
                    "straightLineSpeedMetresPerSec": 22.352,
                    "straightLineDistanceMultiplier": 1.0
                }
            }
        }
        """
        req = self.client.send_model(self.base_json, self.model_id)
        print(req)
        # req = self.client.send_model(json.loads(test_json), self.model_id)
        # print(req)
        # print(json.dumps(self.base_json, indent=4))
