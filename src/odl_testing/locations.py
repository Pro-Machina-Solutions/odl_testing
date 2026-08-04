class Location:
    """Define a distinct geographical location for an activity

    Parameters
    ----------
    name : str
        A unique identifier for this location
    lat : float
        The latitude of the location
    lon : float
        The longitude of the location
    """

    def __init__(self, name: str, lat: float, lon: float):

        self.name = name
        self.lat = lat
        self.lon = lon

    def _serialize(self) -> dict:
        rtn = {"latitude": self.lat, "longitude": self.lon}
        return rtn

    def __repr__(self):
        return (
            f"<Location: {self.name}. Latitude: {self.lat:.6f},"
            f" Longitude: {self.lon:.6f}>"
        )


class Depot(Location):
    """Define the location from which to dispatch/receive vehicles

    Parameters
    ----------
    name : str
        A unique identifier for this location
    lat : float
        The latitude of the location
    lon : float
        The longitude of the location
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return (
            f"<Depot: {self.name}. Latitude: {self.lat:.6f},"
            f" Longitude: {self.lon:.6f}>"
        )
