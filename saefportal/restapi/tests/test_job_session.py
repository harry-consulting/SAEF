import copy

from django.test import tag
from rest_framework.test import APIClient, APITestCase
from users.models import User
from saef.models import JobSession
from saefportal.settings import MSG_ERROR_INVALID_INPUT, MSG_ERROR_REQUIRED_INPUT, MSG_ERROR_MISSING_OBJECT_INPUT, \
    MSG_ERROR_EXISTING
from utils.test_utils import load_test_json, load_test_database

test_data = load_test_json('restapi')


@tag("celery")
class JobSessionStartTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_database('saef.applicationtoken')
        load_test_database('saef.application')
        load_test_database('saef.applicationsession')
        load_test_database('saef.job')

    def setUp(self):
        self.data = copy.deepcopy(test_data)
        self.user = User.objects.create_user(**self.data['Credentials'])

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_job_status_post_success(self):
        jobs = JobSession.objects.filter().count()
        self.assertEqual(jobs, 0)

        response = self.client.post('http://localhost:8000/restapi/job_sessions/start/', self.data['JobSessionStart'],
                                    format='json')
        self.assertEqual(response.status_code, 200)

        jobs = JobSession.objects.filter().count()
        self.assertEqual(jobs, 1)

    def test_job_status_post_required(self):
        self.data['JobSessionStart'].pop('application_execution_id')
        response = self.client.post('http://localhost:8000/restapi/job_sessions/start/', self.data['JobSessionStart'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'],
                         MSG_ERROR_REQUIRED_INPUT('application_execution_id and job_execution_id'))

    def test_job_status_post_invalid(self):
        self.data['JobSessionStart']['application_execution_id'] = 'notvalid'
        response = self.client.post('http://localhost:8000/restapi/job_sessions/start/', self.data['JobSessionStart'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_INVALID_INPUT('UUID'))

    def test_job_status_post_missing_object(self):
        self.data['JobSessionStart']['application_execution_id'] = '11a1a11a-a11a-1111-1a11-a1a1aaa11111'
        response = self.client.post('http://localhost:8000/restapi/job_sessions/start/', self.data['JobSessionStart'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_MISSING_OBJECT_INPUT("application execution id or job name"))


class JobSessionEndTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_database('saef.applicationtoken')
        load_test_database('saef.application')
        load_test_database('saef.applicationsession')
        load_test_database('saef.job')
        load_test_database('saef.jobsession')

    def setUp(self):
        self.data = copy.deepcopy(test_data)
        self.user = User.objects.create_user(**self.data['Credentials'])

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_job_status_post_success(self):
        jobs = JobSession.objects.filter(execution_id=self.data['JobSessionEnd']['job_execution_id']).count()
        self.assertEqual(jobs, 1)

        response = self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'],
                                    format='json')
        self.assertEqual(response.status_code, 200)

        jobs = JobSession.objects.filter(execution_id=self.data['JobSessionEnd']['job_execution_id']).count()
        self.assertEqual(jobs, 2)

    def test_job_status_post_exist(self):
        self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'], format='json')
        response = self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_EXISTING('job', 'END'))

    def test_job_status_post_required(self):
        self.data['JobSessionEnd'].pop('job_execution_id')
        response = self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_REQUIRED_INPUT('application_execution_id and '
                                                                          'job_execution_id'))

    def test_job_status_post_invalid(self):
        self.data['JobSessionEnd']['job_execution_id'] = 'notvalid'
        response = self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_INVALID_INPUT('UUID'))

    def test_job_status_post_missing_object(self):
        self.data['JobSessionEnd']['job_execution_id'] = '11a1a11a-a11a-1111-1a11-a1a1aaa11111'
        response = self.client.post('http://localhost:8000/restapi/job_sessions/end/', self.data['JobSessionEnd'],
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], MSG_ERROR_MISSING_OBJECT_INPUT("application or job execution id"))
