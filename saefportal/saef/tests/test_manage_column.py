import copy

from django.urls import reverse
from django.test import TestCase

from utils.test_utils import load_test_json, load_test_database, load_test_dataset
from ..models import DatasetMetadataColumn
from users.models import User

from saefportal.settings import MSG_SUCCESS_DATA_SAVE, MSG_SUCCESS_EXTRACT_UNSAVED

test_data = load_test_json('saef')


class ManageColumnDatasetViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_dataset()
        load_test_database('saef.datasetmetadatacolumn')
        
    def setUp(self):
        self.data = copy.deepcopy(test_data)
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email=self.credentials['email'], password=self.credentials['password'])
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])

    def test_manage_column_view_get(self):
        dataset_pk = 1
        response = self.client.get(reverse('manage_column', args=(dataset_pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_column/manage_column.html')

    def test_manage_column_submit_undo(self):
        test_pk = 1

        self.data['ManageColumnTableFormset']["Operation"] = 'Undo'
        response = self.client.post(f'/saef/column/manage/{test_pk}/',
                                    self.data['ManageColumnTableFormset'], follow=True)

        self.assertRedirects(response, f'/saef/column/manage/{test_pk}/')

    def test_manage_column_submit_form_extraction_replace(self):
        test_pk = 1

        # Before submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 10)
        self.assertEqual(result[0].column_name, 'BusinessEntityID')

        self.data['ManageColumnTableFormset']["datasetmetadatacolumn_set-0-column_name"] = 'changed'
        response = self.client.post(f'/saef/column/manage/{test_pk}/',
                                    self.data['ManageColumnTableFormset'], follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_DATA_SAVE)
        
        # After submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 3)
        self.assertEqual(result[0].column_name, 'changed')

    def test_manage_column_submit_form_add(self):
        test_pk = 1

        # Before submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 10)
        self.assertEqual(result[0].column_name, 'BusinessEntityID')

        self.data['ManageColumnTableFormset']["Extraction"] = ''
        response = self.client.post(f'/saef/column/manage/{test_pk}/', self.data['ManageColumnTableFormset'],
                                    follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_DATA_SAVE)
        
        # After submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 13)
        self.assertEqual(result[10].column_name, 'id')

    def test_manage_column_submit_form_extracting_retrieve(self):
        test_pk = 1

        # Before submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 10)
        self.assertEqual(result[0].column_name, 'BusinessEntityID')

        self.data['ManageColumnTableFormset']["Operation"] = 'Extract scheme'
        response = self.client.post(f'/saef/column/manage/{test_pk}/', self.data['ManageColumnTableFormset'],
                                    follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_EXTRACT_UNSAVED)
        
        # # After submitting form
        result = DatasetMetadataColumn.objects.filter(dataset=test_pk)
        self.assertIsNotNone(result)
        self.assertEquals(len(result), 10)
        self.assertEqual(result[0].column_name, 'BusinessEntityID')

        self.assertEquals(response.context['difference'][0]['Column name']['status'], 'changes')
        self.assertEquals(response.context['difference'][0]['Data type']['status'], 'changes')
        self.assertEquals(response.context['difference'][0]['Is null']['status'], 'nothing')

        self.assertEquals(len(response.context['formset']), 5)
