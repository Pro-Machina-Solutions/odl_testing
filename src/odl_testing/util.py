import datetime as dt


def convert_to_model_time(timestamp: str) -> str:
    # TODO think about converting timezones to UTC for timezone-aware inputs
    stamp = dt.datetime.isoformat(dt.datetime.fromisoformat(timestamp))
    return stamp
