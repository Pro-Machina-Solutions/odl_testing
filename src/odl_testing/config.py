import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config:
    def __init__(
        self,
        road_network_time_multiplier: float = 1.0,
        use_road_network: bool = False,
        straight_line_speed_metres_per_sec: float = 22.352,
        straight_line_distance_multiplier: float = 1.0,
    ):
        self.username = os.environ["USER_NAME"]
        self.password = os.environ["USER_PASS"]

        self.road_network_time_multiplier = road_network_time_multiplier
        self.use_road_networks = use_road_network
        self.straight_line_speed_metres_per_sec = (
            straight_line_speed_metres_per_sec
        )
        self.straight_line_distance_multiplier = (
            straight_line_distance_multiplier
        )

    def _serialize(self):
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
