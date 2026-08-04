import base64
from typing import Any

from .config import Config
from .model import Model


class Client:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config if config is not None else Config()
        auth = base64.b64encode(
            (f"{self.config.username}:{self.config.password}").encode()
        ).decode("utf-8")
        self.auth_header = {"Authorization": f"Basic {auth}"}

    def send_model(self, model: Model):
        pass

    def get_req(self, body: dict[Any, Any]):
        pass

    def push_req(self, body: dict[Any, Any]):
        pass

    def del_req(self, body: dict[Any, Any]):
        pass
