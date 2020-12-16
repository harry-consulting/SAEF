from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from utils.test_utils import load_test_db

from saef.models import JobSession, JobSessionMetaData
from analyzer.tasks.task_compute_job_session_meta_data import task_compute_job_session_meta_data


def delete_job_sessions(pk_range):
    for pk in pk_range:
        JobSession.objects.filter(pk=pk).delete()


class ComputeJobSessionMetaDataTest(TestCase):
    def setUp(self):
        load_test_db("analyzer", "test_compute_job_session_meta_data")

    def compute_job_session_meta_data_test(self, pk_range, pk, status_type):
        delete_job_sessions(pk_range)
        job_session_start = JobSession.objects.get(pk=pk)
        self.assertRaises(ObjectDoesNotExist, JobSessionMetaData.objects.get,
                          job_session__pk=job_session_start.pk)

        task_compute_job_session_meta_data(job_session_start.pk)
        meta_data = JobSessionMetaData.objects.get(job_session__pk=job_session_start.pk)
        self.assertEquals(meta_data.status_type, status_type)

    def test_should_give_failed_status_type_if_average_delta_is_too_high(self):
        self.compute_job_session_meta_data_test(range(3, 9), 1, "FAILED")

    def test_should_give_failed_status_type_if_actual_execution_time_is_too_high(self):
        self.compute_job_session_meta_data_test(range(7, 9), 5, "FAILED")

    def test_should_give_failed_status_type_if_actual_execution_time_is_too_low(self):
        self.compute_job_session_meta_data_test(range(7, 9), 3, "FAILED")

    def test_should_give_succeed_status_type_if_time_lower_than_deviation_and_max_delta_is_lower_than_threshold(self):
        self.compute_job_session_meta_data_test(range(1, 7), 7, "SUCCEEDED")

    def test_should_give_succeed_with_issue_status_type_else(self):
        self.compute_job_session_meta_data_test(range(1, 9), 9, "SUCCEEDED_ISSUE")
