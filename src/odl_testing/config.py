import os
import warnings
from typing import Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config:
    """Main config parameters for solving VRP problems

    Parameters
    ----------
    base_url : str, optional
        The solver host URL, by default "http://127.0.0.1"
    port : int, optional
        The solver host port, by default 8080
    username : str, optional
        Login username for the solver, by default
        `os.environ.get("USER_NAME")`
    password : str, optional
        Login password for the solver, by default
        os.environ.get("USER_PASS")
    road_network_time_multiplier : float, optional
        Travel time multiplier if using a real road network, by default 1.0
    use_road_network : bool, optional
        Travel distances to use. If not supplied, the Haversine distance
        will be used, by default False
    straight_line_speed_metres_per_sec : float, optional
        Assumed travel speed for Haversine distance, by default 22.352
    straight_line_distance_multiplier : float, optional
        Travel distance multiplier if using Haversine distances, by
        default 1.0
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1",
        port: int = 8080,
        username: str | None = os.environ.get("USER_NAME"),
        password: str | None = os.environ.get("USER_PASS"),
        road_network_time_multiplier: float = 1.0,
        use_road_network: bool = False,
        straight_line_speed_metres_per_sec: float = 22.352,
        straight_line_distance_multiplier: float = 1.0,
    ) -> None:
        self.username = username
        self.password = password

        self._offline = True
        if self.username is None or self.password is None:
            warnings.warn(
                "No login credentials supplied, so problem can only be built"
                " but not dispatched to be solved",
                stacklevel=1,
            )
            self._offline = False

        self.base_url = base_url
        self.port = str(port)

        self.road_network_time_multiplier = road_network_time_multiplier
        self.use_road_networks = use_road_network
        self.straight_line_speed_metres_per_sec = (
            straight_line_speed_metres_per_sec
        )
        self.straight_line_distance_multiplier = (
            straight_line_distance_multiplier
        )

    def _serialize(self) -> dict[Any, Any]:
        rtn = {
            "distances": {
                "roadNetworkTimeMultiplier": self.road_network_time_multiplier,
                "useRoadNetwork": self.use_road_networks,
                "straightLineSpeedMetresPerSec": (
                    self.straight_line_speed_metres_per_sec
                ),
                "straightLineDistanceMultiplier": (
                    self.straight_line_distance_multiplier
                ),
            }
        }
        return rtn
