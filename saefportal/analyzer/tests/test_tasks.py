import os
from datetime import datetime, timedelta

import pandas as pd
from django.core import mail
from model_bakery import baker

from analyzer.tasks import task_extract_metadata, task_profile_dataset, delete_outdated_datalake_files, run_job_task
from datalakes.util import save_data_to_datalake
from util.data_util import get_schema
from util.test_util import ClientLoginDatalakeTestCase


class TaskTests(ClientLoginDatalakeTestCase):
    @classmethod
    def setUpTestData(cls):
        super(TaskTests, cls).setUpTestData()

        cls.dataset = baker.make("datasets.Dataset", name="biostats", type="TABLE")
        cls.user = baker.make("users.User")

        # Download the test data and save it to the temporary test datalake.
        cls.df = pd.read_csv("database/data/test/biostats.csv")
        save_data_to_datalake(cls.df, get_schema(cls.df), cls.dataset.get_datalake_path())

    def test_profile_dataset_first_run(self):
        """The first profile run of a dataset should always have a degree of change of 0."""
        dataset_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Profile dataset")
        task_result = task_profile_dataset(dataset_run=dataset_run)

        self.assertEqual(task_result["degree_of_change"], 0)

    def test_profile_dataset(self):
        # Do the first profile run with the original biostats data.
        first_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Profile dataset")
        task_profile_dataset(dataset_run=first_run)

        # Load changed biostats data into the datalake where the "Weight(lbs)" column is removed.
        df = self.df.drop(labels="Weight(lbs)", axis=1)
        save_data_to_datalake(df, get_schema(df), self.dataset.get_datalake_path())

        # Do the second run with the changed data, resulting in a non-zero degree of change.
        second_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Profile dataset")
        task_result = task_profile_dataset(dataset_run=second_run)

        self.assertEqual(task_result["degree_of_change"], 0.015873015873015872)

    def test_extract_metadata(self):
        dataset_run = baker.make("datasets.DatasetRun", dataset=self.dataset, task_name="Extract metadata")
        task_result = task_extract_metadata(dataset_run=dataset_run)

        self.assertIn("timestamp", task_result)
        self.assertEqual(task_result["column_count"], 5)
        self.assertEqual(task_result["row_count"], 18)
        self.assertEqual(task_result["columns"], {"Name": "object", "Sex": "object", "Age": "int64",
                                                  "Height(in)": "int64", "Weight(lbs)": "int64"})

    def test_delete_outdated_datalake_files(self):
        now = datetime.now()
        data_folder = "test_datalake/saef/landing/uploads/biostats/data"

        # Save multiple versions of the dataset, each version timestamped an hour earlier.
        for i in range(1, 3):
            time = now - timedelta(hours=i)
            save_data_to_datalake(self.df, get_schema(self.df), self.dataset.get_datalake_path(), time=time)

        self.assertEqual(len(os.listdir(data_folder)), 3)

        # Deleting outdated datalake files should delete the 2 versions that are older than an hour.
        delete_outdated_datalake_files(60)

        self.assertEqual(len(os.listdir(data_folder)), 1)

    def test_run_email_on_start(self):
        job = baker.make("jobs.Job", template_task="EXTRACT_METADATA", alert_on_start_email="test@example.com")
        run_job_task(job.id, self.user.email, {"dataset_key": str(self.dataset.key)})

        self.assertIn("start", mail.outbox[0].subject)

    def test_run_email_on_success(self):
        job = baker.make("jobs.Job", template_task="EXTRACT_METADATA", alert_on_success_email="test@example.com")
        run_job_task(job.id, self.user.email, {"dataset_key": str(self.dataset.key)})

        self.assertIn("success", mail.outbox[0].subject)

    def test_run_email_on_failure(self):
        # Setting the datalake to None temporarily to make the task run fail.
        self.settings.datalake = None
        self.settings.save()

        job = baker.make("jobs.Job", template_task="EXTRACT_METADATA", alert_on_failure_email="test@example.com")
        run_job_task(job.id, self.user.email, {"dataset_key": str(self.dataset.key)})

        # Reassigning the datalake for use in subsequent tests.
        self.settings.datalake = self.datalake
        self.settings.save()

        self.assertIn("failure", mail.outbox[0].subject)
