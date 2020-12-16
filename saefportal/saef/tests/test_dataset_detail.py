from django.test import TestCase
from django.urls import reverse

from utils.test_utils import load_test_db


class DatasetDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db('saef', 'test_dataset_detail')
        
    def setUp(self):
        self.client.login(email='t@test.com', password='test')
        
    def get_response(self, test_pk):
        return self.client.get(reverse('dataset_session', args=(test_pk,)))
        
    def test_view_get(self):
        test_pk = 1 
        response = self.get_response(test_pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dataset_overview/dataset_detail.html')

    def test_recent_datasets(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(response.context['metadata'].pk, test_pk)
        self.assertEqual(len(response.context['recent_dataset_sessions_metadata']), 3)
        
    def test_dataset_actual_profile(self):
        test_pk = 1
        response = self.get_response(test_pk)
        self.assertEqual(response.context['actual_dataset_profile'].dataset_session.pk, test_pk)
        
    def test_dataset_profile_does_not_exist(self):
        test_pk = 3
        response = self.get_response(test_pk)
        
        self.assertContains(response, 'No actual columns found')
        
    def test_job_does_not_exist(self):
        test_pk = 10
        response = self.get_response(test_pk)
        
        self.assertContains(response, 'Dataset session not found')
        
