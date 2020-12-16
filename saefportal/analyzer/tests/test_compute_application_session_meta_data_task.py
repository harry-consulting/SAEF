from analyzer.tasks.task_compute_application_session_meta_data import task_compute_application_session_meta_data
from django.core.exceptions import ObjectDoesNotExist
from django.test import TransactionTestCase
from utils.test_utils import load_test_db

from saef.models import ApplicationSession, ApplicationSessionMetaData


def setUpDatabase():
    load_test_db("analyzer", "test_compute_application_session_meta_data_task")


def delete_application_sessions(pk_range):
    for pk in pk_range:
        ApplicationSession.objects.filter(pk=pk).delete()


class ComputeApplicationSessionMetaDataTaskTest(TransactionTestCase):
    def setUp(self):
        setUpDatabase()

    def compute_application_session_meta_data_test(self, pk_range, pk, status_type):
        delete_application_sessions(pk_range)
        application_session_start = ApplicationSession.objects.get(pk=pk)
        self.assertRaises(ObjectDoesNotExist, ApplicationSessionMetaData.objects.get,
                          application_session__pk=application_session_start.pk)

        task_compute_application_session_meta_data(application_session_start.pk)
        meta_data = ApplicationSessionMetaData.objects.get(application_session__pk=application_session_start.pk)
        self.assertEquals(meta_data.status_type, status_type)

    def test_should_give_failed_status_type_if_average_delta_is_too_high(self):
        self.compute_application_session_meta_data_test(range(3, 9), 1, "FAILED")

    def test_should_give_failed_status_type_if_actual_execution_time_is_too_high(self):
        self.compute_application_session_meta_data_test(range(5, 9), 3, "FAILED")

    def test_should_give_failed_status_type_if_actual_execution_time_is_too_low(self):
        self.compute_application_session_meta_data_test(range(5, 9), 1, "FAILED")

    def test_should_give_succeed_status_type_if_time_lower_than_deviation_and_max_delta_is_lower_than_threshold(self):
        self.compute_application_session_meta_data_test(range(1, 5), 5, "SUCCEEDED")

    def test_should_give_succeed_with_issue_status_type_else(self):
        self.compute_application_session_meta_data_test(range(1, 7), 7, "SUCCEEDED_ISSUE")
