import datetime as dt


def convert_to_model_time(timestamp: dt.datetime):
    # TODO think about converting timezones to UTC for timezone-aware inputs
    stamp = dt.datetime.fromisocalendar()
    return stamp.isocalendar()
