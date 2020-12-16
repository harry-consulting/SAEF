import copy

from django.test import TestCase
from django.urls import reverse

from saef.forms import Dataset
from users.models import User
from utils.test_utils import load_test_json, load_test_db

test_data = load_test_json('saef')

SELECT_CONNECTION_TEMPLATE_NAME = 'dataset/select_connection.html'
ADD_DATASET_TEMPLATE_NAME = 'dataset/dataset_add.html'


class AddDatasetViewTests(TestCase):
    def assertDatasetStructuralEquivalence(self, actual_dataset, expected_dataset, expected_sql,
                                           expected_dataset_access_method, expected_table):
        self.assertEqual(actual_dataset["connection"], str(expected_dataset.connection.pk))
        self.assertEqual(actual_dataset["job"], str(expected_dataset.job.pk))
        self.assertEqual(actual_dataset["sequence_in_job"], str(expected_dataset.sequence_in_job))
        self.assertEqual(actual_dataset["dataset_name"], str(expected_dataset.dataset_name))
        self.assertEqual(actual_dataset["dataset_type"], str(expected_dataset.dataset_type))
        self.assertEqual(actual_dataset["query_timeout"], str(expected_dataset.query_timeout))
        self.assertEqual(expected_dataset_access_method, expected_dataset.dataset_access_method)
        self.assertEqual(expected_sql, expected_dataset.dataset_extraction_sql)
        self.assertEqual(expected_table, expected_dataset.dataset_extraction_table)

    @classmethod
    def setUpTestData(cls):
        load_test_db("saef", "test_add_dataset")

    def setUp(self):
        self.data = copy.deepcopy(test_data)
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email=self.credentials['email'], password=self.credentials['password'])
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])

    def test_dataset_create_view_get(self):
        response = self.client.get(reverse('add_dataset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SELECT_CONNECTION_TEMPLATE_NAME)

    def test_show_add_dataset_page_if_valid_connection_is_chosen(self):
        response = self.client.post(reverse('add_dataset'), self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ADD_DATASET_TEMPLATE_NAME)

    def test_do_not_show_add_dataset_page_if_invalid_connection_is_chosen(self):
        self.data['DatasetForm']['connection'] = 1
        response = self.client.post(reverse('add_dataset'), self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SELECT_CONNECTION_TEMPLATE_NAME)

    def test_save_dataset_with_table_extraction_method_successfully(self):
        self.data['DatasetForm']['dataset_extraction_sql'] = ''
        self.data['DatasetForm']['Operation'] = 'Save'

        response = self.client.post(reverse('add_dataset'), self.data['DatasetForm'], follow=True)
        expected_dataset = Dataset.objects.get(dataset_name=self.data['DatasetForm']['dataset_name'])

        self.assertEqual(response.status_code, 200)
        self.assertDatasetStructuralEquivalence(self.data["DatasetForm"], expected_dataset, None, "TABLE",
                                                self.data["DatasetForm"]["dataset_extraction_table"])
        self.assertRedirects(response, reverse("saef_dataset"))

    def test_save_dataset_with_sql_extraction_method_successfully(self):
        self.data['DatasetForm']['dataset_access_method'] = 'SQL'
        self.data['DatasetForm']['dataset_extraction_table'] = ''
        self.data['DatasetForm']['Operation'] = 'Save'

        response = self.client.post(reverse('add_dataset'), self.data['DatasetForm'], follow=True)
        expected_dataset = Dataset.objects.get(dataset_name=self.data['DatasetForm']['dataset_name'])

        self.assertEqual(response.status_code, 200)
        self.assertDatasetStructuralEquivalence(self.data["DatasetForm"], expected_dataset,
                                                self.data["DatasetForm"]["dataset_extraction_sql"], "SQL", None)
        self.assertRedirects(response, reverse("saef_dataset"))

    def test_do_not_save_dataset_if_dataset_is_invalid(self):
        self.data["DatasetForm"]["dataset_name"] = ''
        self.data["DatasetForm"]["Operation"] = "Save"

        response = self.client.post(reverse('add_dataset'), self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ADD_DATASET_TEMPLATE_NAME)
