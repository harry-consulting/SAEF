from django.test import TestCase
from django.urls import reverse

from utils.test_utils import load_test_db


class JobDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db('saef', 'test_job_detail')
        
    def setUp(self):
        self.client.login(email='t@test.com', password='test')
        
    def get_response(self, test_pk):
        return self.client.get(reverse('job_session', args=(test_pk,)))
        
    def test_view_get(self):
        test_pk = 1 
        response = self.get_response(test_pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'job_overview/job_detail.html')

        self.assertEqual(response.context['metadata'].pk, test_pk)

    def test_recent_jobs(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(len(response.context['recent_job_sessions_metadata']), 2)
        
    def test_dataset_sessions_metadata(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(len(response.context['dataset_sessions_metadata']), 3)
        
    def test_dataset_sessions_does_not_exist(self):
        test_pk = 3
        response = self.get_response(test_pk)
        
        self.assertContains(response, 'No dataset sessions found')
        
    def test_job_does_not_exist(self):
        test_pk = 10
        response = self.get_response(test_pk)
        
        self.assertContains(response, 'Job session not found')
        
