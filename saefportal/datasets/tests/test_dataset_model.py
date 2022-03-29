from decouple import config
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from datasets.models import Dataset
from util.test_util import ClientLoginDatalakeTestCase, create_linked_jobs


class DatasetModelTests(ClientLoginDatalakeTestCase):
    @classmethod
    def setUpTestData(cls):
        super(DatasetModelTests, cls).setUpTestData()

        cls.datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                                   username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                                   password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

        cls.connection = baker.make("datasets.Connection", name="owned connection", owner=cls.user,
                                    datastore=cls.datastore)

    def test_filename_validator(self):
        """Datasets should not be able to be created with a name that cannot be a filename."""
        form_data = {"name": "invalid / name:", "query": "SELECT * FROM humanresources.employee",
                     "connection": self.connection.id, "owner": self.user.id, "type": "QUERY"}
        response = self.client.post(reverse("datasets:create_query_dataset"), form_data, follow=True)

        self.assertContains(response, "Name cannot be used as a folder name in the datalake.")
        self.assertFalse(Dataset.objects.filter(name="invalid / name:").exists())

    def test_connection_dataset_unique_together(self):
        """Datasets should not be able to be created with the same name as another dataset from the same connection."""
        baker.make("datasets.Dataset", name="humanresources.employee", type="TABLE", table="humanresources.employee",
                   connection=self.connection)

        # Should raise the "Name uniqueness" integrity error when trying to create another dataset with the same name.
        self.assertRaises(IntegrityError, baker.make, "datasets.Dataset", name="humanresources.employee", type="TABLE",
                          table="humanresources.employee", connection=self.connection)

    def test_get_linked_jobs(self):
        """
        If the dataset key is in the schedule parameters or last used parameters of a job, the job should be included
        in the linked jobs.
        """
        dataset = baker.make("datasets.Dataset", name="test dataset", owner=self.user)
        scheduled_job, manual_job = create_linked_jobs(self.user, dataset.key)

        linked_jobs = dataset.get_linked_jobs()
        self.assertIn(scheduled_job, linked_jobs)
        self.assertIn(manual_job, linked_jobs)

    def test_get_degree_of_change_data(self):
        """If a dataset has been profiled, the profile runs should be included in the degree of change chart data."""
        dataset = baker.make("datasets.Dataset", name="test dataset", owner=self.user)

        kwargs = {"dataset": dataset, "task_name": "Profile dataset"}
        run_1 = baker.make("datasets.DatasetRun", **kwargs, result={"degree_of_change": 0})
        run_2 = baker.make("datasets.DatasetRun", **kwargs, result={"degree_of_change": 10})

        result = dataset.get_degree_of_change_data()
        self.assertIn({"x": int(run_1.start_datetime.strftime("%s")) * 1000, "y": 0, "id": run_1.id}, result)
        self.assertIn({"x": int(run_2.start_datetime.strftime("%s")) * 1000, "y": 10, "id": run_2.id}, result)
