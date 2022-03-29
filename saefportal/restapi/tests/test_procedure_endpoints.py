from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import User


class ProcedureTests(APITestCase):
    def setUp(self):
        self.credentials = {"email": "test@test.com", "password": "test"}
        self.user = User.objects.create_user(email=self.credentials["email"], password=self.credentials["password"])
        self.client.force_authenticate(user=self.user)

    def test_profile_dataset_missing_arguments(self):
        response = self.client.post(reverse("profile-dataset"), data={})
        error_detail = response.data["dataset_key"][0]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_detail, ErrorDetail(string="This field is required.", code="required"))

    def test_refresh_data_missing_arguments(self):
        response = self.client.post(reverse("refresh-data"), data={})
        error_detail = response.data["dataset_key"][0]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_detail, ErrorDetail(string="This field is required.", code="required"))

    def test_extract_metadata_missing_arguments(self):
        response = self.client.post(reverse("extract-metadata"), data={})
        error_detail = response.data["dataset_key"][0]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_detail, ErrorDetail(string="This field is required.", code="required"))

    def test_read_data_missing_arguments(self):
        response = self.client.post(reverse("read-data"), data={})

        key_error_detail = response.data["dataset_key"][0]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(key_error_detail, ErrorDetail(string="This field is required.", code="required"))
