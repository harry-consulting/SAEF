from django.test import TestCase
from django.urls import reverse

from utils.test_utils import load_test_database, load_test_db


class ApplicationDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db('saef', 'test_application_detail')

    def setUp(self):
        self.client.login(email='t@test.com', password='test')
        
    def get_response(self, test_pk):
        return self.client.get(reverse('application_session', args=(test_pk,)))
        
    def test_application_detail_view_get(self):
        test_pk = 1 
        response = self.get_response(test_pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_overview/application_detail.html')

        self.assertEqual(response.context['metadata'].pk, test_pk)

    def test_application_detail_recent_applications(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(len(response.context['recent_application_sessions_metadata']), 3)
        
    def test_application_detail_job_sessions_metadata(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(len(response.context['job_sessions_metadata']), 3)
        
    def test_application_detail_run_info_jobs(self):
        test_pk = 1
        response = self.get_response(test_pk)
        
        self.assertEqual(response.context['succeeded_jobs'], 1)
        self.assertEqual(response.context['total_jobs'], 3)
        
    def test_application_detail_does_not_exist(self):
        test_pk = 10
        response = self.get_response(test_pk)
        
        self.assertContains(response, 'Application session not found')