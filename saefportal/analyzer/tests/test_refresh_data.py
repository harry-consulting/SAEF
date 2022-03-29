import os
import time

from decouple import config
from model_bakery import baker

from analyzer.tasks import task_refresh_data, task_refresh_all_datasets
from util.test_util import ClientLoginDatalakeTestCase


class RefreshDataTests(ClientLoginDatalakeTestCase):
    """Separate test class for the refresh data task tests since this task requires a datastore connection."""

    @classmethod
    def setUpTestData(cls):
        super(RefreshDataTests, cls).setUpTestData()

        datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                               username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                               password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

        # Create a dataset with a connection which automatically saves a snapshot of the dataset to the datalake.
        cls.connection = baker.make("datasets.Connection", datastore=datastore, name="postgres")
        cls.dataset = baker.make("datasets.Dataset", name="employee", type="TABLE", table="humanresources.employee",
                                 connection=cls.connection)

        cls.data_folder = "test_datalake/saef/landing/postgres/employee/data"

    def setUp(self):
        """Sleeping for half a second before each test to ensure the time-based filenames are not overwritten."""
        time.sleep(0.5)

    def test_refresh_data(self):
        initial_file_count = len(os.listdir(self.data_folder))

        dataset_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Refresh data")
        task_result = task_refresh_data(dataset_run=dataset_run, task_parameters={})

        # After refreshing, the data folder should contain one more snapshot of the data.
        self.assertTrue(task_result["refreshed"])
        self.assertEqual(len(os.listdir(self.data_folder)), initial_file_count + 1)

    def test_refresh_data_degree_of_change_below_threshold(self):
        """
        If a degree of change threshold is specified, the data should not be refreshed if the actual degree of change is
        below or equal to the threshold.
        """
        initial_file_count = len(os.listdir(self.data_folder))

        # Since the degree of change should be 0, the data should not be refreshed.
        dataset_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Refresh data")
        task_result = task_refresh_data(dataset_run=dataset_run, task_parameters={"degree_of_change_threshold": 0.05})

        # The data folder should contain the same amount of files as before the task run.
        self.assertFalse(task_result["refreshed"])
        self.assertEqual(len(os.listdir(self.data_folder)), initial_file_count)

    def test_refresh_data_degree_of_change_above_threshold(self):
        """
        If a degree of change threshold is specified, the data should be refreshed if the actual degree of change is
        above the threshold.
        """
        initial_file_count = len(os.listdir(self.data_folder))

        # Since the degree of change should be 0, the data should be refreshed.
        dataset_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Refresh data")
        task_result = task_refresh_data(dataset_run=dataset_run, task_parameters={"degree_of_change_threshold": -1})

        # After refreshing, the data folder should contain one more snapshot of the data.
        self.assertTrue(task_result["refreshed"])
        self.assertEqual(len(os.listdir(self.data_folder)), initial_file_count + 1)

    def test_refresh_all_datasets(self):
        department_data_folder = "test_datalake/saef/landing/postgres/department/data"

        # Create another dataset with the same connection.
        baker.make("datasets.Dataset", name="department", type="TABLE", table="humanresources.department",
                   connection=self.connection)

        initial_employee_count = len(os.listdir(self.data_folder))
        initial_department_count = len(os.listdir(department_data_folder))

        task_refresh_all_datasets()

        # After refreshing, both data folders should contain one more snapshot of the data.
        self.assertEqual(len(os.listdir(self.data_folder)), initial_employee_count + 1)
        self.assertEqual(len(os.listdir(department_data_folder)), initial_department_count + 1)
