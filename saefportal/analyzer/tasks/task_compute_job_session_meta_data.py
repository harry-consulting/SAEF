from __future__ import absolute_import, unicode_literals

from analyzer.models import DatasetSession
from analyzer.tasks.util import save_job_session_meta_data_without_status_type, get_status_type
from saef.models import JobSession
from restapi.util import calculate_execution_time, calculate_expected_time


def task_compute_job_session_meta_data(job_session_start_pk):
    job_session_start = JobSession.objects.get(pk=job_session_start_pk)

    job_filter = {'job__pk': job_session_start.job.id, 'status_type': 'END'}
    actual_execution_time = calculate_execution_time(job_session_start.execution_id, JobSession)
    expected_execution_time = calculate_expected_time(job_session_start.job.id, JobSession, job_filter)

    meta_data = save_job_session_meta_data_without_status_type(job_session_start, actual_execution_time,
                                                               expected_execution_time)
    dataset_session_queryset = DatasetSession.objects.filter(job_session__pk=job_session_start_pk)

    meta_data.status_type = get_status_type(dataset_session_queryset, meta_data)
    meta_data.save()

    return {"actual_execution_time": str(actual_execution_time),
            "expected_execution_time": str(expected_execution_time)}
