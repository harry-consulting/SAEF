import copy

import uuid
from rest_framework import status
from rest_framework.test import APIClient

from utils.test_utils import load_test_json, load_test_db
from users.models import User
from saef.models import ApplicationSession

from django.test import TransactionTestCase, tag
from analyzer.celery_conf import app
from celery.contrib.testing.worker import start_worker

test_data = load_test_json('restapi')

class TestEndApplicationSession(TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db("restapi", "test_application_session")

    @classmethod
    def setUpClass(cls):
       super().setUpClass()
       cls.celery_worker = start_worker(app)
       cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
       super().tearDownClass()
       cls.celery_worker.__exit__(None, None, None)

    def setUp(self):
        self.setUpTestData()
        self.data = copy.deepcopy(test_data)
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(**self.credentials)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.application_session = ApplicationSession.objects.get(pk=3)
        self.end_data = {
            "execution_id": self.application_session.execution_id,
            "status_time": "2020-06-29 16:00+0100"
        }

    def test_should_end_application_session(self):
        self.assertEqual(
            ApplicationSession.objects.filter(execution_id=self.application_session.execution_id).count(),
            1
        )
        self.end_data["execution_id"] = self.application_session.execution_id
        response = self.client.post("http://localhost:8000/restapi/application_sessions/end/",
                                    data=self.end_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ApplicationSession.objects.filter(execution_id=self.application_session.execution_id).count(),
            2
        )
        application_sessions = ApplicationSession.objects.filter(execution_id=self.application_session.execution_id)

        self.assertEqual(len(list(filter(lambda x: x.status_type == "START", application_sessions))), 1)
        self.assertEqual(len(list(filter(lambda x: x.status_type == "END", application_sessions))), 1)

    def test_should_not_end_with_empty_post_data(self):
        response = self.client.post('http://localhost:8000/restapi/application_sessions/end/', data={}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Request has an invalid format")

    def test_should_not_end_application_session_twice(self):
        first_response = self.client.post('http://localhost:8000/restapi/application_sessions/end/',
                                          data=self.end_data, format='json')
        second_response = self.client.post('http://localhost:8000/restapi/application_sessions/end/',
                                           data=self.end_data, format='json')

        self.assertEqual(first_response.status_code, 200)

        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(second_response.data["error"], "Application session has already ended")

    def test_should_not_end_with_invalid_execution_id(self):
        self.end_data["execution_id"] = "Invalid execution id"
        response = self.client.post('http://localhost:8000/restapi/application_sessions/end/',
                                    data=self.end_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Request has an invalid format")

    def test_should_not_end_with_nonexisting_execution_id(self):
        self.end_data["execution_id"] = str(uuid.uuid4())
        response = self.client.post('http://localhost:8000/restapi/application_sessions/end/',
                                    data=self.end_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Invalid execution id")

    def test_should_not_end_with_invalid_status_time(self):
        self.end_data["status_time"] = "Invalid status time"
        response = self.client.post('http://localhost:8000/restapi/application_sessions/end/',
                                    data=self.end_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Request has an invalid format")
