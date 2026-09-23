import datetime as dt
import json
import random
from string import ascii_letters

from odl_testing import (
    Depot,
    Location,
    Model,
    Service,
    Vehicle,
    VehicleAct,
    VehicleType,
)

# Set the geofence boundaries for the random jobs
MIN_LAT = 12.491
MAX_LAT = 12.546
MIN_LON = -70.014
MAX_LON = -69.937

# How many jobs do we want in the problem? For now, they are just Service jobs
# so have no capacity constraints
NUM_LOCATIONS = 20

# We can set a time window for when our problem spans. For now, we'll just
# cover one shift
START_TIME = "2026-08-07 09:00:00"
END_TIME = "2026-08-07 18:00:00"

# Internal plumbing to make sure the job times always fall within the shift we
# just chose and nothing is raised 30 mins before the end of the shift
MAX_SERVICE_WINDOW = (
    dt.datetime.fromisoformat(END_TIME) - dt.datetime.fromisoformat(START_TIME)
).total_seconds() - 9000

# How long do we need to be at each service job location?
SERVICE_TIMES = [random.randint(30, 100) * 1000 for _ in range(NUM_LOCATIONS)]

# Decide a span on the acceptable time window for each job
TIME_WINDOW_HOURS = 2

JOB_STARTS = [
    dt.datetime.fromisoformat(START_TIME)
    + dt.timedelta(seconds=random.randint(0, int(MAX_SERVICE_WINDOW)))
    for _ in range(NUM_LOCATIONS)
]

model = Model()

depot = Depot(
    name="depot",
    lat=random.uniform(MIN_LAT, MAX_LAT),
    lon=random.uniform(MIN_LON, MAX_LON),
)

locations = [
    Location(
        name="".join(random.choices(ascii_letters, k=5)),
        lat=random.uniform(MIN_LAT, MAX_LAT),
        lon=random.uniform(MIN_LON, MAX_LON),
    )
    for _ in range(NUM_LOCATIONS)
]

# Build the jobs
for i, loc in enumerate(locations):
    model.add_job(
        Service(
            name=loc.name,
            location=loc,
            duration=SERVICE_TIMES[i],
            open_time=JOB_STARTS[i].isoformat(),
            close_time=(
                JOB_STARTS[i] + dt.timedelta(hours=TIME_WINDOW_HOURS)
            ).isoformat(),
        )
    )

# Create the  vehicles
generic_vehicle = VehicleType()
for i in range(2):
    model.add_vehicle(
        Vehicle(
            name=str(i),
            start_time=START_TIME,
            end_time=END_TIME,
            late_time=END_TIME,
            start_type=VehicleAct.START_AT_DEPOT,
            end_type=VehicleAct.END_AT_DEPOT,
            start_location=depot,
            end_location=depot,
            vtype=generic_vehicle,
        )
    )

model.build()

print(json.dumps(model._base_json, indent=4))
print(model.model_id)
# send = model.send()
