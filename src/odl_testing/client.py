import base64
from typing import Any

import requests

from .config import Config


class Client:
    """Object used to communicate with the ODL Live instance"""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config if config is not None else Config()
        auth = base64.b64encode(
            (f"{self.config.username}:{self.config.password}").encode()
        ).decode("utf-8")
        self.auth_header = {"Authorization": f"Basic {auth}"}
        self.url = f"{self.config.base_url}:{self.config.port}/models"

    def test(self) -> requests.Response | None:
        if not self.config._offline:
            req = requests.get(self.url, headers=self.auth_header)
            return req
        else:
            return None

    def send_model(self, model: dict[Any, Any], model_id: str):
        url = f"{self.url}/{model_id}"
        query = requests.put(url, json=model, headers=self.auth_header)

        print(query)

    def get_req(self, body: dict[Any, Any]):
        pass

    def push_req(self, body: dict[Any, Any]):
        pass

    def del_req(self, body: dict[Any, Any]):
        pass
