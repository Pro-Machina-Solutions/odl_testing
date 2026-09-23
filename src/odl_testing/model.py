import uuid
from typing import Any

from .client import Client
from .config import Config
from .jobs import _Job
from .vehicles import Vehicle


class Model:
    """Container class to hold all of the objects in the problem definition

    Parameters
    ----------
    config : Config | None, optional
        A custom config object containing such things as algorithm behaviour in
        regards to road speed/distance calculations etc. as well as the
        connection credentials and endpoint for the ODL Live instance. if no
        config is supplied, the default settings will be used.
    """

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
        self.client = Client(config=self.config)
        self.model_id = uuid.uuid4().hex

    def add_job(self, job: _Job) -> None:
        """Add an instance of a Service, Pickup or Delivery to the problem

        Parameters
        ----------
        job : _Job
            A Service, Pickup or Delivery

        Raises
        ------
        TypeError
            The job added is not a Service, Pickup or a Delivery
        """
        if not isinstance(job, _Job):
            raise TypeError("Incorrect job type")
        self.jobs.append(job._serialize())

    def add_vehicle(self, vehicle) -> None:
        """Add a Vehicle instance to the problem

        Parameters
        ----------
        vehicle : Vehicle
            A defined Vehicle instance with associated running costs

        Raises
        ------
        TypeError
            Something other than a Vehicle was passed
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Incorrect vehicle type")
        self.vehicles.append(vehicle._serialise())

    def build(self) -> dict[str, Any]:
        """Prepare the payload of the Model to be sent to ODL Live.

        Returns
        -------
        dict[str, Any]
            The completed payload that will be sent to the solver
        """
        # TODO for now we just send the same JSON object back, but we might
        # need to add other modifications required in future
        return self._base_json

    def send(self) -> dict[str, Any]:
        """Dispatch the model to the solver.

        If there are no login credentials for ODL Live then the payload will be
        returned and no further action is taken. However, if the credentials
        are available, the problem will first be dispatched to the solver and
        then the payload will be sent.

        Returns
        -------
        dict[str, Any]
            The Model defined as a JSON payload
        """
        if self.config._offline:
            return self._base_json
        else:
            self.client.send_model(
                model=self._base_json, model_id=self.model_id
            )
        return self._base_json
