import copy
from django.test import override_settings

from rest_framework.test import APIClient
from users.models import User
from saef.models import DatasetSession
from saefportal.settings import MSG_ERROR_INVALID_INPUT, MSG_ERROR_REQUIRED_INPUT, MSG_ERROR_MISSING_OBJECT_INPUT, \
    MSG_ERROR_EXISTING
from utils.test_utils import load_test_json, load_test_db
from django.test import TransactionTestCase
from analyzer.celery_conf import app
from celery.contrib.testing.worker import start_worker

test_data = load_test_json('restapi')


def setUpTestDatabase():
    load_test_db('restapi', 'test_dataset_session')


class DatasetSessionStartTests(TransactionTestCase):
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
        super().setUp()
        setUpTestDatabase()

        self.data = copy.deepcopy(test_data)
        self.user = User.objects.create_user(**self.data['Credentials'])

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_dataset_status_post_success(self):
        dataset_sessions = DatasetSession.objects.filter().count()
        self.assertEqual(dataset_sessions, 0)

        response = self.client.post('http://localhost:8000/restapi/dataset_session/calculate/',
                                    self.data['DatasetSessionCalculate'], format='json',
                                    timeout=(5, 120))
        self.assertEqual(response.status_code, 200)

        dataset_sessions = DatasetSession.objects.filter().count()
        self.assertEqual(dataset_sessions, 1)

    def test_dataset_status_post_required(self):
        self.data['DatasetSessionCalculate'].pop('job_execution_id')
        response = self.client.post('http://localhost:8000/restapi/dataset_session/calculate/',
                                    self.data['DatasetSessionCalculate'], format='json',
                                    timeout=(5, 120))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_REQUIRED_INPUT('job_execution_id and name'))

    def test_dataset_status_post_invalid(self):
        self.data['DatasetSessionCalculate']['job_execution_id'] = 'notvalid'
        response = self.client.post('http://localhost:8000/restapi/dataset_session/calculate/',
                                    self.data['DatasetSessionCalculate'], format='json',
                                    timeout=(5, 120))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_INVALID_INPUT('UUID'))

    def test_dataset_status_post_missing_object(self):
        self.data['DatasetSessionCalculate']['job_execution_id'] = '11a1a11a-a11a-1111-1a11-a1a1aaa11111'
        response = self.client.post('http://localhost:8000/restapi/dataset_session/calculate/',
                                    self.data['DatasetSessionCalculate'], format='json',
                                    timeout=(5, 120))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_MISSING_OBJECT_INPUT("job execution id or dataset name"))
