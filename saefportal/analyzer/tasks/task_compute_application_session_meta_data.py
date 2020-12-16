from __future__ import absolute_import, unicode_literals

from analyzer.tasks.util import get_dataset_session_queryset, avg, is_failed_status, is_success_status, \
    save_application_session_meta_data_without_status_type, get_status_type
from saef.models import ApplicationSession
from restapi.util import calculate_execution_time, calculate_expected_time


def task_compute_application_session_meta_data(application_session_start_pk):
    application_session_start = ApplicationSession.objects.get(pk=application_session_start_pk)

    application_filter = {'application__pk': application_session_start.application.pk, 'status_type': 'END'}
    actual_execution_time = calculate_execution_time(application_session_start.execution_id, ApplicationSession)
    expected_execution_time = calculate_expected_time(application_session_start.application.pk, ApplicationSession,
                                                      application_filter)

    meta_data = save_application_session_meta_data_without_status_type(application_session_start, actual_execution_time,
                                                                       expected_execution_time)

    dataset_comparison_list = get_dataset_session_queryset(meta_data)

    meta_data.status_type = get_status_type(dataset_comparison_list, meta_data)
    meta_data.save()

    return {"actual_execution_time": str(actual_execution_time),
            "expected_execution_time": str(expected_execution_time)}
