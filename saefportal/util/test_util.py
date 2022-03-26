import json
import shutil

from django.test import TestCase
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from model_bakery import baker

from users.models import User


class ClientLoginTestCase(TestCase):
    """Test case used when the client needs to be logged in."""

    @classmethod
    def setUpTestData(cls):
        cls.credentials = {"email": "test@test.com", "password": "test"}
        cls.user = User.objects.create_user(email=cls.credentials["email"], password=cls.credentials["password"])

    def setUp(self):
        self.client.login(email=self.credentials["email"], password=self.credentials["password"])


class ClientLoginDatalakeTestCase(ClientLoginTestCase):
    """
    Test case used when the client needs to be logged in and an empty local datalake should be created when the
    tests start and deleted when they end.
    """

    @classmethod
    def setUpTestData(cls):
        super(ClientLoginDatalakeTestCase, cls).setUpTestData()

        # Setting up an empty local datalake.
        cls.datalake = baker.make("datalakes.LocalDatalake", root_path="test_datalake")
        cls.settings = baker.make("settings.Settings", try_live_connection=False, datalake=cls.datalake)

    @classmethod
    def tearDownClass(cls):
        super(ClientLoginDatalakeTestCase, cls).tearDownClass()

        shutil.rmtree("test_datalake")


def create_linked_jobs(owner, dataset_key):
    """
    Create and return two jobs that are linked to the given dataset key. One job is linked through the schedule
    parameters and the other through the last run parameters.
    """
    # Adding a scheduled job with the dataset key in its parameters.
    scheduled_job = baker.make("jobs.Job", name="scheduled job", owner=owner)

    kwargs = json.dumps({"task_parameters": {"dataset_key": str(dataset_key)}})
    schedule, _ = CrontabSchedule.objects.get_or_create()
    baker.make(PeriodicTask, name=scheduled_job.id, task="task", kwargs=kwargs, crontab=schedule)

    # Adding a manual job with a job run to simulate it being run with the dataset.
    manual_job = baker.make("jobs.Job", name="manual job", owner=owner)
    baker.make("jobs.JobRun", job=manual_job, parameters={"dataset_key": str(dataset_key)})

    return scheduled_job, manual_job
