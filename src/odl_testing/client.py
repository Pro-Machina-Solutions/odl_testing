import base64
from typing import Any

import requests

from .config import Config


class Client:
    """Object used to communicate with the ODL Live instance"""

    def __init__(self, config: Config) -> None:
        self.config = config
        auth = base64.b64encode(
            (f"{self.config.username}:{self.config.password}").encode()
        ).decode("utf-8")
        self.auth_header = {"Authorization": f"Basic {auth}"}
        self.url = f"{self.config.base_url}:{self.config.port}/models"

    def test(self) -> requests.Response | None:
        """Check that the client can communicate with the server

        Returns
        -------
        requests.Response | None
            If the connection is successful, the server response object will be
            returned. In the case that no connection credentials are provided,
            the method returns None and does not attempt to communicate with
            the server.
        """
        if not self.config._offline:
            req = requests.get(self.url, headers=self.auth_header)
            return req
        else:
            return None

    def send_model(self, model: dict[str, Any], model_id: str) -> int:
        """Dispatch the model to the solver

        Parameters
        ----------
        model : dict[str, Any]
            The dictionary to be passed as JSON to the solver
        model_id : str
            The unique UUID generated for the model

        Returns
        -------
        int
            The status code of the server submission
        """
        url = f"{self.url}/{model_id}"
        query = requests.put(url, json=model, headers=self.auth_header)
        return query.status_code

    def get_req(self, body: dict[str, Any]):
        # TODO
        pass

    def push_req(self, body: dict[str, Any]):
        # TODO
        pass

    def del_req(self, body: dict[str, Any]):
        # TODO
        pass
