from decouple import config
from django.urls import reverse
from model_bakery import baker

from datalakes.models import LocalDatalake
from datasets.models import Note
from datastores.models import PostgresDatastore
from util.test_util import ClientLoginDatalakeTestCase, create_linked_jobs


class DatasetDetailTests(ClientLoginDatalakeTestCase):
    @classmethod
    def setUpTestData(cls):
        super(DatasetDetailTests, cls).setUpTestData()

        cls.datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                                   username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                                   password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

        cls.connection = baker.make("datasets.Connection", name="owned connection", owner=cls.user,
                                    datastore=cls.datastore)
        cls.dataset = baker.make("datasets.Dataset", name="humanresources.employee", type="TABLE", tags="hr, table",
                                 table="humanresources.employee", connection=cls.connection, owner=cls.user,
                                 description="This is the employee table description.")

    def test_dataset_detail_table(self):
        """When on a dataset's detail page, information about the dataset should be shown."""
        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "humanresources.employee")
        self.assertContains(response, "This is the employee table description.")
        self.assertContains(response, "hr, table")

    def test_valid_connection_definition(self):
        """When a valid connection is available, the dataset's column types and a data preview should be shown."""
        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "Column types")
        self.assertContains(response, "Data preview")

    def test_invalid_connection_definition(self):
        """
        When the data overview cannot be retrieved from the datastore or datalake, an appropriate error message
        should be displayed.
        """
        # Make the datastore and datalake connections invalid.
        PostgresDatastore.objects.filter(host=config("TEST_POSTGRES_HOST")).update(host="Invalid host")
        LocalDatalake.objects.filter(root_path="test_datalake").update(root_path="")

        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "A live connection could not be made and no historic data overviews are "
                                      "available.")

        # Revert the datastore and datalake to make them valid for other tests.
        PostgresDatastore.objects.filter(host="Invalid host").update(host=config("TEST_POSTGRES_HOST"))
        LocalDatalake.objects.filter(root_path="").update(root_path="test_datalake")

    def test_profile_runs(self):
        """When the dataset has been profiled, information about the profile runs should be shown."""
        baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Profile dataset")
        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "Number of profiles:")

    def test_no_profile_runs(self):
        """When the dataset has not yet been profiled, an appropriate message should be displayed."""
        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "No profile runs are available.")

    def test_linked_jobs(self):
        """
        If a job exists which has the dataset key in its schedule parameters or the last used parameters, it should
        be shown in the linked jobs tab.
        """
        scheduled_job, manual_job = create_linked_jobs(self.user, self.dataset.key)

        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, scheduled_job.name)
        self.assertContains(response, manual_job.name)

    def test_no_linked_jobs(self):
        """If no linked jobs exist, an appropriate message should be displayed."""
        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.id}))

        self.assertContains(response, "The dataset is not linked to any jobs.")

    def test_create_note(self):
        """If a note is created, it should be shown in the dataset detail."""
        data = {"dataset_id": self.dataset.id, "note_text": "test note text"}
        self.client.post(reverse("datasets:create_note"), data)

        response = self.client.get(reverse("datasets:dataset_detail", kwargs={"pk": self.dataset.pk}))
        self.assertContains(response, "test note text")

    def test_delete_note(self):
        """If a note is deleted, it should be removed from the dataset detail."""
        note = baker.make("datasets.Note", text="test note text", dataset=self.dataset, created_by=self.user)

        data = {"dataset_id": self.dataset.id, "note_id": note.id}
        self.client.delete(reverse("datasets:delete_note", kwargs=data))

        self.assertFalse(Note.objects.filter(text="test note text").exists())
