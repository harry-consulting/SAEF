import copy
from django.test import TestCase
from django.urls import reverse

from ..models import DatasetMetadataConstraint
from utils.test_utils import load_test_json, load_test_database, load_test_dataset
from users.models import User

from saefportal.settings import MSG_SUCCESS_DATA_SAVE

test_data = load_test_json('saef')

class TestManageConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_dataset()
        load_test_database('saef.datasetmetadataconstraint')
        cls.dataset_id = 1

    def setUp(self) -> None:
        self.data = copy.deepcopy(test_data)
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email=self.credentials['email'], password=self.credentials['password'])
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])


    def test_get_manage_constraint_view(self):
        response = self.client.get(reverse("manage_constraint", kwargs={"dataset_id": self.dataset_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_constraint/manage_constraint.html")

    def test_manage_constraint_submit_undo(self):
        self.data["ManageConstraintTableFormSet"]["Operation"] = "Undo"
        response = self.client.post(reverse("manage_constraint", kwargs={"dataset_id": self.dataset_id}),
                                    self.data["ManageConstraintTableFormSet"], follow=True)
        self.assertRedirects(response, reverse("manage_constraint", kwargs={"dataset_id": self.dataset_id}))

    def test_should_successfully_add_extracted_constraints(self):
        result = DatasetMetadataConstraint.objects.filter(dataset=self.dataset_id)
        self.assertEqual(len(result), 1)

        response = self.client.post(reverse("manage_constraint", kwargs={"dataset_id": self.dataset_id}),
                                    self.data["ManageConstraintTableFormSet"], follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_DATA_SAVE)

        result = DatasetMetadataConstraint.objects.filter(dataset=self.dataset_id)
        self.assertEqual(len(result), 3)

    def test_should_successfully_add_constraints(self):
        result = DatasetMetadataConstraint.objects.filter(dataset=self.dataset_id)
        self.assertEqual(len(result), 1)

        self.data["ManageConstraintTableFormSet"]["Extraction"] = ""

        response = self.client.post(reverse("manage_constraint", kwargs={"dataset_id": self.dataset_id}),
                                    self.data["ManageConstraintTableFormSet"], follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_DATA_SAVE)

        result = DatasetMetadataConstraint.objects.filter(dataset=self.dataset_id)
        self.assertEqual(len(result), 4)