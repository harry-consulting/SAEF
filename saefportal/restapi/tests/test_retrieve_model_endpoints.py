import shutil

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from restapi.tests.util import create_test_data
from users.models import User


class ListRetrieveModelTests(APITestCase):
    """
    Simple tests for the basic list and retrieve endpoints. Note that when filtering the result, the list endpoints
    should only show the objects that the user has permission for. If the user does not have permission for an object,
    the retrieve endpoints should return an error. Permission is given through ownership in this case.
    """

    @classmethod
    def setUpTestData(cls):
        credentials = {"email": "test@test.com", "password": "test"}
        cls.user = User.objects.create_user(email=credentials["email"], password=credentials["password"])

        create_test_data(cls.user)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @classmethod
    def tearDownClass(cls):
        super(ListRetrieveModelTests, cls).tearDownClass()

        shutil.rmtree("test_datalake")

    def test_list_organization_groups(self):
        response = self.client.get(reverse("organizationgroup-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "All")
        self.assertContains(response, "Admin")

    def test_list_object_permissions(self):
        response = self.client.get(reverse("objectpermission-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "connection")
        self.assertContains(response, "dataset")

    def test_list_connections(self):
        """Should only show the connections that the user has permission for."""
        response = self.client.get(reverse("connection-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "connection 1")
        self.assertNotContains(response, "connection 2")

    def test_list_postgres_datastores(self):
        """Should only show Postgres datastores related to the connections that the user has permission for."""
        response = self.client.get(reverse("postgresdatastore-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "postgres 1")
        self.assertNotContains(response, "postgres 2")

    def test_list_azure_datastores(self):
        """Should only show Azure datastores related to the connections that the user has permission for."""
        response = self.client.get(reverse("azuredatastore-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "azure 1")
        self.assertNotContains(response, "azure 2")

    def test_list_datasets(self):
        """Should only show datasets that the user has permission for."""
        response = self.client.get(reverse("dataset-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "dataset 1")
        self.assertNotContains(response, "dataset 2")

    def test_list_dataset_runs(self):
        """Should only show dataset runs related to the datasets that the user has permission for."""
        response = self.client.get(reverse("datasetrun-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "938c276c-b2ab-4410-9142-af7d1054bfc2")
        self.assertNotContains(response, "71672ac1-7038-4ed9-a8b6-81794a8d239f")

    def test_list_notes(self):
        """Should only show notes related to the datasets that the user has permission for."""
        response = self.client.get(reverse("note-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "note 1")
        self.assertNotContains(response, "note 2")

    def test_list_jobs(self):
        """Should only show jobs that the user has permission for."""
        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "job 1")
        self.assertNotContains(response, "job 2")

    def test_list_job_runs(self):
        """Should only show job runs related to the jobs that the user has permission for."""
        response = self.client.get(reverse("jobrun-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "65cf3c6c-dabd-4256-b068-d717de40375d")
        self.assertNotContains(response, "99dd1a79-e4f0-4311-8d79-44b5ce5402e5")

    def test_list_contacts(self):
        response = self.client.get(reverse("contact-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "contact 1")
        self.assertContains(response, "contact 2")

    def test_list_users_no_admin(self):
        """If the user is not an admin user, the user list should be forbidden."""
        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_admin(self):
        # Change the logged-in user to an admin user.
        self.client.logout()
        admin = User.objects.create_superuser(email="admin@test.com", password="test")
        self.client.force_authenticate(user=admin)

        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "test@test.com")
        self.assertContains(response, "test2@test.com")

    def test_retrieve_organization(self):
        response = self.client.get(reverse("organization-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "organization 1")

    def test_retrieve_organization_group(self):
        response = self.client.get(reverse("organizationgroup-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "All")

    def test_retrieve_object_permission(self):
        response = self.client.get(reverse("objectpermission-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "connection")
        self.assertContains(response, "1")

    def test_retrieve_connection(self):
        response = self.client.get(reverse("connection-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "connection 1")

    def test_retrieve_connection_no_permission(self):
        response = self.client.get(reverse("connection-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_postgres_datastore(self):
        response = self.client.get(reverse("postgresdatastore-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "postgres 1")

    def test_retrieve_postgres_datastore_no_permission(self):
        response = self.client.get(reverse("postgresdatastore-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_azure_datastore(self):
        response = self.client.get(reverse("azuredatastore-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "azure 1")

    def test_retrieve_azure_datastore_no_permission(self):
        response = self.client.get(reverse("azuredatastore-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_dataset(self):
        response = self.client.get(reverse("dataset-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "dataset 1")

    def test_retrieve_dataset_no_permission(self):
        response = self.client.get(reverse("dataset-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_dataset_run(self):
        response = self.client.get(reverse("datasetrun-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "938c276c-b2ab-4410-9142-af7d1054bfc2")

    def test_retrieve_dataset_run_no_permission(self):
        response = self.client.get(reverse("datasetrun-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_note(self):
        response = self.client.get(reverse("note-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "note 1")

    def test_retrieve_note_no_permission(self):
        response = self.client.get(reverse("note-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_job(self):
        response = self.client.get(reverse("job-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "job 1")

    def test_retrieve_job_no_permission(self):
        response = self.client.get(reverse("job-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_job_run(self):
        response = self.client.get(reverse("jobrun-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "65cf3c6c-dabd-4256-b068-d717de40375d")

    def test_retrieve_job_run_no_permission(self):
        response = self.client.get(reverse("job-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_contact(self):
        response = self.client.get(reverse("contact-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "contact 1")

    def test_retrieve_settings(self):
        response = self.client.get(reverse("settings-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "UTC")

    def retrieve_user_no_admin(self):
        response = self.client.get(reverse("user-detail", args=[2]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_user_admin(self):
        # Change the logged-in user to an admin user.
        self.client.logout()
        admin = User.objects.create_superuser(email="admin@test.com", password="test")
        self.client.force_authenticate(user=admin)

        response = self.client.get(reverse("user-detail", args=[self.user.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "test@test.com")
