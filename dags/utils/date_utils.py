from datetime import datetime
import pytz #type:ignore


def is_earlier(ts1_str, ts2_str):
    """returns whether the first timestamp is an earlier date from the second timestamp

    Args:
        ts1_str (timestamp): first timestamp/date
        ts2_str (timestamp): second timestamp/date

    Returns:
        bool: ts1<ts2
    """
    ts1 = datetime.strptime(ts1_str, "%Y-%m-%dT%H:%M:%S")
    tz_uz = pytz.timezone("Asia/Tashkent")  # UTC+5
    ts1 = tz_uz.localize(ts1)

    # Parse ts2 (ISO 8601 with timezone)
    ts2 = datetime.strptime(ts2_str, "%Y-%m-%dT%H:%M:%S%z")

    # Compare
    return ts1 < ts2