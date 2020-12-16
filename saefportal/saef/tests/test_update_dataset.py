import copy

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from ..models import Dataset
from utils.test_utils import load_test_json, load_test_db
from users.models import User

test_data = load_test_json('saef')

EDIT_DATASET_TEMPLATE_NAME = 'dataset/dataset_detail.html'
PREVIEW_DATASET_TEMPLATE_NAME = 'dataset/dataset_preview.html'


class ManageEditDatasetViewTests(TestCase):
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
        load_test_db("saef", "test_update_dataset")

    def setUp(self):
        self.data = copy.deepcopy(test_data)
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email=self.credentials['email'], password=self.credentials['password'])
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])

    def test_dataset_edit_view_get(self):
        dataset_id = 1
        response = self.client.get(reverse('dataset_detail', kwargs={"dataset_id": dataset_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)

    def test_should_contain_table_list_if_switching_to_valid_connection(self):
        dataset_id = 1
        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data["DatasetForm"])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)
        self.assertIsNot(len(response.context["edit_form"].fields["dataset_extraction_table"].choices), 0)

    def test_should_not_contain_table_list_if_switching_to_invalid_connection(self):
        dataset_id = 12
        del self.data["DatasetForm"]["connection"]
        self.data["DatasetForm"]["connection"] = 1
        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data["DatasetForm"])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)
        self.assertIs(len(response.context["edit_form"].fields["dataset_extraction_table"].choices), 0)

    def test_should_delete_dataset(self):
        dataset_id = 12
        self.data["DatasetForm"]["Operation"] = "Delete"
        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data["DatasetForm"], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("saef_dataset"))
        self.assertRaises(ObjectDoesNotExist, Dataset.objects.get, id=12)

    def test_successfully_update_dataset_with_table_extraction_method(self):
        dataset_id = 11
        self.data['DatasetForm']['dataset_extraction_sql'] = "SQL Query"
        self.data['DatasetForm']['Operation'] = 'Save'

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'], follow=True)
        expected_dataset = Dataset.objects.get(dataset_name=self.data['DatasetForm']['dataset_name'])

        self.assertEqual(response.status_code, 200)
        self.assertDatasetStructuralEquivalence(self.data["DatasetForm"], expected_dataset, "SQL Query",
                                                "TABLE", self.data["DatasetForm"]["dataset_extraction_table"])
        self.assertRedirects(response, reverse("saef_dataset"))

    def test_successfully_update_dataset_with_sql_extraction_method(self):
        dataset_id = 11
        self.data['DatasetForm']['dataset_access_method'] = 'SQL'
        self.data['DatasetForm']['Operation'] = 'Save'

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'], follow=True)
        expected_dataset = Dataset.objects.get(dataset_name=self.data['DatasetForm']['dataset_name'])

        self.assertEqual(response.status_code, 200)
        self.assertDatasetStructuralEquivalence(self.data["DatasetForm"], expected_dataset,
                                                self.data["DatasetForm"]["dataset_extraction_sql"], "SQL",
                                                "public.saef_job")
        self.assertRedirects(response, reverse("saef_dataset"))

    def test_do_not_update_dataset_if_form_is_invalid(self):
        dataset_id = 11
        self.data["DatasetForm"]["dataset_name"] = ''
        self.data["DatasetForm"]["Operation"] = "Save"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)

    def test_should_redirect_to_manage_column_page_if_manage_column_button_is_pressed(self):
        dataset_id = 11
        self.data["DatasetForm"]["Operation"] = "Manage Column"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("manage_column", kwargs={"dataset_id": dataset_id}))

    def test_should_redirect_to_manage_constraint_page_if_manage_constraint_button_is_pressed(self):
        dataset_id = 11
        self.data["DatasetForm"]["Operation"] = "Manage Constraint"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("manage_constraint", kwargs={"dataset_id": dataset_id}))

    def test_should_preview_if_query_is_correct(self):
        dataset_id = 11
        self.data["DatasetForm"]["Operation"] = "Preview"
        self.data["DatasetForm"]["dataset_access_method"] = "SQL"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PREVIEW_DATASET_TEMPLATE_NAME)

    def test_should_not_preview_if_query_contains_syntax_error(self):
        dataset_id = 13
        self.data["DatasetForm"]["Operation"] = "Preview"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)

    def test_should_not_preview_if_query_references_incorrect_table_name(self):
        dataset_id = 14
        self.data["DatasetForm"]["Operation"] = "Preview"

        response = self.client.post(reverse("dataset_detail", kwargs={"dataset_id": dataset_id}),
                                    self.data['DatasetForm'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_DATASET_TEMPLATE_NAME)
