from decouple import config
from django.urls import reverse
from model_bakery import baker
from notifications.models import Notification

from datasets.models import Connection, Dataset
from jobs.models import Job
from users.models import PermissionRequest, ObjectPermission
from util.test_util import ClientLoginTestCase, ClientLoginDatalakeTestCase


class ResourceAccessTests(ClientLoginTestCase):
    @classmethod
    def setUpTestData(cls):
        super(ResourceAccessTests, cls).setUpTestData()

        baker.make("users.OrganizationGroup", name="Admin")
        cls.all_group = baker.make("users.OrganizationGroup", name="All")

        cls.job = baker.make("jobs.Job", name="job 1", owner=cls.user)
        cls.level_2_perm = ObjectPermission.objects.get(object_id=cls.job.id, can_update=True)

    def test_create_permission_request(self):
        form_data = {"permission-select": [self.level_2_perm.id]}
        response = self.client.post(reverse("request_access"), form_data, follow=True)

        created_request = PermissionRequest.objects.filter(permission=self.level_2_perm)
        self.assertTrue(created_request.exists())
        self.assertEqual(response.context["incoming_requests"], [created_request.first()])

        # The owner of the requested permissions' resource should get a notification.
        self.assertTrue(Notification.objects.filter(recipient=self.job.owner).exists())

    def test_view_full_permission_request(self):
        permission_request = PermissionRequest.objects.create(requesting_user=self.user, permission=self.level_2_perm,
                                                              group=self.all_group, message="Test request")

        response = self.client.get(reverse("permission_request", args=[permission_request.id]))

        self.assertContains(response, self.level_2_perm)
        self.assertContains(response, self.user)
        self.assertContains(response, self.all_group)
        self.assertContains(response, "Pending")
        self.assertContains(response, "Test request")

    def test_decline_permission_request(self):
        permission_request = PermissionRequest.objects.create(requesting_user=self.user, permission=self.level_2_perm)

        form_data = {"reply": "false", "permission_request_id": permission_request.id}
        self.client.post(reverse("reply_to_request"), form_data)

        permission_request.refresh_from_db()
        self.assertEqual(PermissionRequest.Status.DECLINED, permission_request.status)

        # The user that made the request should get a notification.
        self.assertTrue(Notification.objects.filter(recipient=permission_request.requesting_user))

    def test_accept_permission_request(self):
        permission_request = PermissionRequest.objects.create(requesting_user=self.user, permission=self.level_2_perm)

        form_data = {"reply": "true", "permission_request_id": permission_request.id}
        self.client.post(reverse("reply_to_request"), form_data)

        permission_request.refresh_from_db()
        self.assertEqual(PermissionRequest.Status.ACCEPTED, permission_request.status)

        # The user that made the request should get a notification.
        self.assertTrue(Notification.objects.filter(recipient=permission_request.requesting_user))


class ConnectionAccessTests(ClientLoginDatalakeTestCase):
    """
    When trying to update or delete a connection that the user does not have the proper permissions for,
    it should redirect to the permission request modal.
    """

    @classmethod
    def setUpTestData(cls):
        super(ConnectionAccessTests, cls).setUpTestData()

        baker.make("users.OrganizationGroup", name="Admin")
        cls.connection = baker.make("datasets.Connection", name="connection 1", owner=baker.make("users.User"))
        cls.owned_connection = baker.make("datasets.Connection", name="Connection 2", owner=cls.user)

    def test_update_connection_no_permission(self):
        response = self.client.get(reverse("datasets:update_connection", args=[self.connection.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_update_connection_with_permission(self):
        response = self.client.get(reverse("datasets:update_connection", args=[self.owned_connection.id]))

        self.assertContains(response, "Update connection")

    def test_delete_connection_no_permission(self):
        response = self.client.get(reverse("datasets:delete_connection", args=[self.connection.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_delete_connection_with_permission(self):
        self.client.get(reverse("datasets:delete_connection", args=[self.owned_connection.id]))

        self.assertFalse(Connection.objects.filter(id=self.owned_connection.id).exists())


class DatasetAccessTests(ClientLoginDatalakeTestCase):
    """
    When trying to view, update or delete a dataset the user does not have the proper permissions for,
    it should redirect to the permission request modal.
    """

    @classmethod
    def setUpTestData(cls):
        super(DatasetAccessTests, cls).setUpTestData()

        baker.make("users.OrganizationGroup", name="Admin")
        cls.user_2 = baker.make("users.User")

        cls.datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                                   username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                                   password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

        cls.connection = baker.make("datasets.Connection", name="owned connection", owner=cls.user_2,
                                    datastore=cls.datastore)

        cls.dataset = baker.make("datasets.Dataset", name="dataset 1", type="TABLE", owner=cls.user_2,
                                 table="humanresources.employee", connection=cls.connection)
        cls.owned_dataset = baker.make("datasets.Dataset", name="dataset 2", type="TABLE", owner=cls.user,
                                       table="humanresources.employee", connection=cls.connection)

    def test_view_dataset_no_permission(self):
        response = self.client.get(reverse("datasets:dataset_detail", args=[self.dataset.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_view_dataset_with_permission(self):
        response = self.client.get(reverse("datasets:dataset_detail", args=[self.owned_dataset.id]))

        self.assertContains(response, "dataset 2")

    def test_update_dataset_no_permission(self):
        response = self.client.get(reverse("datasets:update_dataset", args=[self.dataset.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_update_dataset_with_permission(self):
        response = self.client.get(reverse("datasets:update_dataset", args=[self.owned_dataset.id]))

        self.assertContains(response, "Update dataset")

    def test_delete_dataset_no_permission(self):
        response = self.client.get(reverse("datasets:delete_dataset", args=[self.dataset.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_delete_dataset_with_permission(self):
        self.client.get(reverse("datasets:delete_dataset", args=[self.owned_dataset.id]))

        self.assertFalse(Dataset.objects.filter(id=self.owned_dataset.id).exists())


class JobAccessTests(ClientLoginTestCase):
    """
    When trying to view, update, delete or execute a job the user does not have the proper permissions for,
    it should redirect to the permission request modal.
    """

    @classmethod
    def setUpTestData(cls):
        super(JobAccessTests, cls).setUpTestData()

        baker.make("users.OrganizationGroup", name="Admin")

        cls.job = baker.make("jobs.Job", name="job 1", owner=baker.make("users.User"))
        cls.owned_job = baker.make("jobs.Job", name="job 2", owner=cls.user, template_task="PROFILE_DATASET")

    def test_view_job_no_permission(self):
        response = self.client.get(reverse("jobs:run_history", args=[self.job.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_view_job_with_permission(self):
        response = self.client.get(reverse("jobs:run_history", args=[self.owned_job.id]))

        self.assertContains(response, "Job run history")

    def test_update_job_no_permission(self):
        response = self.client.get(reverse("jobs:update", args=[self.job.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_update_job_with_permission(self):
        response = self.client.get(reverse("jobs:update", args=[self.owned_job.id]))

        self.assertContains(response, "Update job")

    def test_delete_job_no_permission(self):
        response = self.client.get(reverse("jobs:delete", args=[self.job.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_delete_job_with_permission(self):
        self.client.get(reverse("jobs:delete", args=[self.owned_job.id]))

        self.assertFalse(Job.objects.filter(id=self.owned_job.id).exists())

    def test_execute_job_no_permission(self):
        response = self.client.get(reverse("jobs:trigger", args=[self.job.id]), follow=True)

        self.assertContains(response, "Permission request")

    def test_execute_job_with_permission(self):
        response = self.client.get(reverse("jobs:trigger", args=[self.owned_job.id]))

        self.assertContains(response, "Trigger job")
