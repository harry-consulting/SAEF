import json
import datetime


def calculate_average(value):
    if len(value) == 0:
        return None

    if is_number(value[0]):
        return calculate_average_number(value)
    elif isinstance(value[0], datetime.date):
        return calculate_average_datetime(value)


def calculate_average_number(values):
    return sum(values) / len(values)


def calculate_average_datetime(values):
    sum_time = sum(map(datetime.datetime.timestamp, values))
    timezone = values[0].tzinfo
    average_timestamp = datetime.datetime.fromtimestamp(sum_time / len(values), tz=timezone)
    return average_timestamp.replace(tzinfo=values[0].tzinfo)


def validate_date(date_text):
    try:
        if type(date_text) is str:
            return datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        return False
    return False


def add_value(previous, value):
    """ Appends the correct datatype to the list."""
    if value is not None:
        if validate_date(value):
            previous.append(validate_date(value))
        elif is_number(value):
            previous.append(is_number(value))

    return previous


def is_number(value):
    try:
        if isinstance(value, (int, float, complex)):
            return value
        if type(value) == str:
            return float(value)
    except ValueError:
        return False
    except TypeError:
        return False


def calculate_hash_sum(data):
    hash_sum = 0
    json_dump = json.dumps(data, default=datetime_encoder).encode('utf-8')

    for v in json_dump:
        hash_sum += v

    return hash_sum


def datetime_encoder(obj):
    """Default JSON serializer."""

    if isinstance(obj, datetime.datetime):
        return str(obj.isoformat())

    raise TypeError('Not sure how to serialize %s' % (obj,))
