import bisect
from datetime import datetime, timedelta

from rest_framework_tracking.models import APIRequestLog

from jobs.models import JobRun


def get_api_usage_data():
    api_data = [request.requested_at.replace(tzinfo=None, microsecond=0) for request in APIRequestLog.objects.all()]

    return get_usage_data(api_data)


def get_job_usage_data():
    job_data = [job_run.start_datetime.replace(tzinfo=None, microsecond=0) for job_run in JobRun.objects.all()]

    return get_usage_data(job_data)


def get_usage_data(data):
    """Convert the given list of usage datetimes into usage data that can be used to populate a line chart."""
    usage_data = insert_into_timeframes(data)
    labels = get_usage_data_labels(usage_data)

    # Convert the usage data and labels to format that can be used to populate a line chart.
    formatted_usage_data = {}
    for timeframe, timeframe_data in usage_data.items():
        count_list = [group["count"] for group in timeframe_data]
        formatted_usage_data[timeframe] = {"labels": labels[timeframe], "data": count_list}

    return formatted_usage_data


def insert_into_timeframes(data):
    """
    Return dict from timeframes to lists of data point counts within the timeframes. The dict contains the timeframes
    "day", "week", "month" and "year". For example, the "week" key returns a list specifying how many data points there
    are in each of the last 7 days.
    """
    current_datetime = datetime.now()

    # Initialize each timeframe with the groups that points should be assigned to.
    timeframes = {"day": initialize_timeframe([timedelta(hours=i) for i in range(23, -1, -1)], "day"),
                  "week": initialize_timeframe([timedelta(days=i) for i in range(6, -1, -1)], "week"),
                  "month": initialize_timeframe([timedelta(days=i) for i in range(29, -1, -1)], "month"),
                  "year": initialize_timeframe([timedelta(days=i * 30) for i in range(11, -1, -1)], "year")}

    # Keep track of the length of each timeframe.
    timeframe_length = {"day": timedelta(days=1), "week": timedelta(days=7), "month": timedelta(days=30),
                        "year": timedelta(days=365)}

    # Assign each point within the timeframe to the specific group that it belongs to.
    for timeframe, timeframe_data in timeframes.items():
        min_time = current_datetime - timeframe_length[timeframe]
        points_within_timeframe = list(filter(lambda x: x > min_time, data))

        datetimes = list(timeframe_data)
        for point in points_within_timeframe:
            # Finding the group a point belongs to by finding the group datetime that is immediately lower.
            insert_point = bisect.bisect(datetimes, point)

            # Increment the point counter of the group which the point belongs to.
            if insert_point != 0:
                timeframe_data[datetimes[insert_point - 1]] += 1

        timeframes[timeframe] = [{"datetime": date_time, "count": count} for date_time, count in timeframe_data.items()]

    return timeframes


def initialize_timeframe(timedeltas, timeframe):
    """
    Return dict from rounded timestamps, covering the given timeframe, initialized with 0 as the point count. Each
    timestamp represents a group within the timeframe (fx. 7 day groups for week data).
    """
    return {round_down(datetime.now() - time_delta, timeframe): 0 for time_delta in timedeltas}


def round_down(dt, timeframe):
    """Round a datetime object down based on the given timeframe."""
    day = 1 if timeframe == "year" else dt.day
    hour = 0 if timeframe in ["year", "month", "week"] else dt.hour

    return dt.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)


def get_usage_data_labels(usage_data):
    """Return dict with human readable labels for each of the groups in each of the given usage data timeframes."""
    labels = {}
    timeframe_formats = {"day": "%H", "week": "%b %d", "month": "%b %d", "year": "%b %Y"}

    for timeframe, timeframe_data in usage_data.items():
        labels[timeframe] = [group["datetime"].strftime(timeframe_formats[timeframe]) for group in timeframe_data]

    # Modify hourly labels to signify that it is covering a period of an hour.
    labels["day"] = [f"{label}:00-{int(label) + 1:02}:00" for label in labels["day"]]

    return labels
