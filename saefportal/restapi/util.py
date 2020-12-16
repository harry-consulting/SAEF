import datetime


def calculate_execution_time(execution_id, Object):
    session_execution = Object.objects.filter(execution_id=execution_id)

    time = {}
    for session in session_execution:
        time[session.status_type] = session.create_timestamp

    if "END" not in time:
        return datetime.timedelta(milliseconds=0)

    return time["END"] - time['START']


def calculate_expected_time(application_id, Object, query_filter):
    sessions = Object.objects.filter(**query_filter).order_by('-create_timestamp')

    if sessions is None or len(sessions) == 0:
        return "Unavailable"
    else:
        return _sum_execution_time(sessions[:10], Object)


def _sum_execution_time(sessions, Object):
    total_execution_time = datetime.timedelta(milliseconds=0)
    for session in sessions:
        total_execution_time += calculate_execution_time(session.execution_id, Object)
    return total_execution_time / len(sessions)


def validate_data(name, data):
    if name in data and data[name] != '':
        return data[name]
    else:
        raise ValueError
