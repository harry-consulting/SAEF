from saefportal.settings import DEVIATION_TIME_SPAN, DATASET_DELTA_THRESHOLD, DATASET_DELTA_DEVIATION, \
    EXPECTED_DATASETS_N
from saef.models import ApplicationSession, ApplicationSessionMetaData, JobSessionMetaData, DatasetSession, \
    DatasetSessionMetaData
from saef.enums import MonitorStatus


def is_failed_status(meta_data, average_delta):
    difference = meta_data.expected_execution_time * DEVIATION_TIME_SPAN
    upper_bound = meta_data.expected_execution_time + difference
    lower_bound = meta_data.expected_execution_time - difference

    if meta_data.actual_execution_time > upper_bound or meta_data.actual_execution_time < lower_bound:
        return True
    elif average_delta > DATASET_DELTA_THRESHOLD:
        return True
    else:
        return False


def get_dataset_session_queryset(meta_data):
    application_session = ApplicationSession.objects.get(
        applicationsessionmetadata__application_session=meta_data.application_session)
    return DatasetSession.objects.filter(job_session__application_session__pk=application_session.pk)


def avg(values):
    return sum(values) / len(values) if len(values) > 0 else 0


def is_success_status(max_delta):
    return max_delta < DATASET_DELTA_THRESHOLD


def save_application_session_meta_data_without_status_type(application_session, actual_execution_time,
                                                           expected_execution_time):
    application_session_meta_data = ApplicationSessionMetaData(
        application_session=application_session,
        actual_execution_time=actual_execution_time,
        expected_execution_time=expected_execution_time
    )
    application_session_meta_data.save()
    return application_session_meta_data


def save_job_session_meta_data_without_status_type(job_session, actual_execution_time, expected_execution_time):
    job_session_meta_data = JobSessionMetaData(
        job_session=job_session,
        actual_execution_time=actual_execution_time,
        expected_execution_time=expected_execution_time
    )
    job_session_meta_data.save()
    return job_session_meta_data


def get_status_type(session_queryset, meta_data):
    session_queryset = filter(lambda x: x.degree_of_change is not None, session_queryset)
    degree_of_change_list = set(map(lambda x: x.degree_of_change, session_queryset))
    average_delta = avg(degree_of_change_list)
    max_delta = max(degree_of_change_list) if len(degree_of_change_list) > 0 else 0

    if is_failed_status(meta_data, average_delta):
        status = MonitorStatus.FAILED.value
    elif is_success_status(max_delta):
        status = MonitorStatus.SUCCEEDED.value
    else:
        status = MonitorStatus.SUCCEEDED_ISSUE.value

    return status


def dataset_session_failed(degree_of_change):
    return degree_of_change > DATASET_DELTA_THRESHOLD


def dataset_session_succeed_with_issue(degree_of_change, dataset_session):
    dataset_sessions = DatasetSession.objects.filter(job_session__application_session__pk=dataset_session.
                                                     job_session.application_session.pk).\
                                                     order_by("-create_timestamp")[:EXPECTED_DATASETS_N]

    dataset_sessions = filter(lambda x: x.degree_of_change is not None, dataset_sessions)
    list_of_degree_of_change = [*map(lambda x: x.degree_of_change, dataset_sessions)]
    historical_average_of_degree_of_change = sum(list_of_degree_of_change) / len(list_of_degree_of_change)

    difference = historical_average_of_degree_of_change * DATASET_DELTA_DEVIATION
    upper_bound = historical_average_of_degree_of_change + difference

    return upper_bound < degree_of_change


def get_dataset_session_status_type(degree_of_change, dataset_session):
    if dataset_session_failed(degree_of_change):
        return MonitorStatus.FAILED.value
    elif dataset_session_succeed_with_issue(degree_of_change, dataset_session):
        return MonitorStatus.SUCCEEDED_ISSUE.value
    else:
        return MonitorStatus.SUCCEEDED.value


def create_dataset_session_meta_data(degree_of_change, dataset_session_pk):
    dataset_session = DatasetSession.objects.get(pk=dataset_session_pk)
    status = get_dataset_session_status_type(degree_of_change, dataset_session)
    DatasetSessionMetaData.objects.create(
        dataset_session=dataset_session,
        status_type=status
    )
