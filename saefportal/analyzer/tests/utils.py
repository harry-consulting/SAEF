from datetime import datetime


def validate_configuration(configuration_dict):
    missing_configuration = []
    for key, value in configuration_dict.items():
        if not value:
            missing_configuration.append(key)

    if len(missing_configuration) > 0:
        raise ValueError(
            f'Missing configuration of {missing_configuration} in the settings.ini file')


def make_naive(value):
    aware_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f%z")
    return (aware_datetime - aware_datetime.utcoffset()).replace(tzinfo=None)
