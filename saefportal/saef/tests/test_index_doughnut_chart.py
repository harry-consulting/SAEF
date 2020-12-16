from datetime import datetime, timedelta

import pytz
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mock import Mock
from utils.test_utils import load_test_db


class IndexDoughnutChart(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db("saef", "test_index_doughnut_chart")

    def setUp(self):
        self.client.login(email="t@test.com", password="test")
        self.date_now_mock = datetime(2020, 8, 25, 15, 37, 26, 179787, tzinfo=pytz.utc)
        timezone.now = Mock(return_value=self.date_now_mock)

    def assert_response_object_equal(self, response, application_session_count, job_session_count,
                                     dataset_session_count):
        self.assertEqual(len(response.context['application_sessions']), application_session_count)
        self.assertEqual(len(response.context['job_sessions']), job_session_count)
        self.assertEqual(len(response.context['dataset_sessions']), dataset_session_count)

    def assert_meta_data_is_gte(self, application_session_meta_data, job_session_meta_data, dataset_session_meta_data,
                                offset):
        for meta_data in application_session_meta_data:
            self.assertGreaterEqual(meta_data.application_session.create_timestamp, offset)
        for meta_data in job_session_meta_data:
            self.assertGreaterEqual(meta_data.job_session.create_timestamp, offset)
        for meta_data in dataset_session_meta_data:
            self.assertGreaterEqual(meta_data.dataset_session.create_timestamp, offset)

    def test_get_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')
        self.assert_response_object_equal(response, 3, 3, 3)

    def test_all_dates_filter(self):
        response = self.client.get(reverse("index") + '?date_option=All+dates')
        self.assertEqual(response.status_code, 200)
        self.assert_response_object_equal(response, 3, 3, 3)

    def test_last_31_days_date_filter(self):
        past_31 = self.date_now_mock + timedelta(days=-31)
        response = self.client.get(reverse("index") + '?date_option=1+month')

        self.assert_response_object_equal(response, 3, 3, 3)
        self.assert_meta_data_is_gte(response.context["application_sessions"],
                                     response.context["job_sessions"],
                                     response.context["dataset_sessions"],
                                     past_31)

    def test_last_7_days_date_filter(self):
        past_7 = self.date_now_mock + timedelta(days=-7)
        response = self.client.get(reverse("index") + "?date_option=7+days")

        self.assert_response_object_equal(response, 0, 0, 0)
        self.assert_meta_data_is_gte(response.context["application_sessions"],
                                     response.context["job_sessions"],
                                     response.context["dataset_sessions"],
                                     past_7)
