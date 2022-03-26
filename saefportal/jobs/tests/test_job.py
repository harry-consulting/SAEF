import ast

from datetime import datetime

from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from model_bakery import baker

from jobs.models import Job
from util.test_util import ClientLoginTestCase


class JobTests(ClientLoginTestCase):
    def setUp(self):
        super(JobTests, self).setUp()

        # Form data to create a manual job.
        self.form_data = {"name": "test job", "owner": self.user.id, "template_task": "REFRESH_DATA",
                          "schedule_start_time": datetime.now().strftime("%Y-%m-%d %H:%M")}

        # Form data to create a periodic job that runs every day at 12:00.
        self.periodic_form_data = {"name": "periodic job", "owner": self.user.id, "template_task": "REFRESH_DATA",
                                   "schedule_start_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                   "schedule-checkbox": "on", "dataset_key": "test key", "cron-input": "0 12 * * *"}

    def test_no_jobs(self):
        """If no jobs exist, an appropriate message should be displayed."""
        response = self.client.get(reverse("jobs:index"))

        self.assertContains(response, "No jobs are available.")
        self.assertQuerysetEqual(response.context["jobs"], [])

    def test_create_job(self):
        response = self.client.post(reverse("jobs:create"), self.form_data, follow=True)

        self.assertContains(response, "test job")
        self.assertTrue(Job.objects.filter(name="test job").exists())

    def test_update_job(self):
        job = baker.make("jobs.Job", name="test job", owner=self.user)

        self.form_data["name"] = "updated test job"
        response = self.client.post(reverse("jobs:update", kwargs={"pk": job.id}), self.form_data, follow=True)

        self.assertContains(response, "updated test job")
        self.assertTrue(Job.objects.filter(name="updated test job").exists())

    def test_create_periodic_job(self):
        """If a periodic job is created, a corresponding periodic task should be created."""
        self.client.post(reverse("jobs:create"), self.periodic_form_data)

        job = Job.objects.get(name="periodic job")
        expected_kwargs = {"job_id": job.id, "user": self.user.email, "task_parameters": {"dataset_key": "test key"}}

        self.assertTrue(PeriodicTask.objects.filter(name=job.id).exists())
        self.assertDictEqual(ast.literal_eval(PeriodicTask.objects.get(name=job.id).kwargs), expected_kwargs)

    def test_update_periodic_job(self):
        """If a periodic job is updated, the corresponding periodic task should also be updated."""
        self.client.post(reverse("jobs:create"), self.periodic_form_data)
        job = Job.objects.get(name="periodic job")

        self.periodic_form_data["dataset_key"] = "new key"
        self.client.post(reverse("jobs:update", kwargs={"pk": job.id}), self.periodic_form_data)

        expected_kwargs = {"job_id": job.id, "user": self.user.email, "task_parameters": {"dataset_key": "new key"}}
        self.assertDictEqual(ast.literal_eval(PeriodicTask.objects.get(name=job.id).kwargs), expected_kwargs)

    def test_make_periodic_job_manual(self):
        """If a periodic job is made manual, the corresponding periodic task should be deleted."""
        self.client.post(reverse("jobs:create"), self.periodic_form_data)
        job = Job.objects.get(name="periodic job")

        # Updating the job with the form data for creating a manual job.
        self.client.post(reverse("jobs:update", kwargs={"pk": job.id}), self.form_data, follow=True)

        self.assertTrue(Job.objects.filter(name="test job").exists())
        self.assertFalse(PeriodicTask.objects.filter(name=job.id).exists())

    def test_delete_job(self):
        """If a job is deleted, both the job and the corresponding periodic task should be deleted."""
        self.client.post(reverse("jobs:create"), self.periodic_form_data)
        job = Job.objects.get(name="periodic job")

        self.client.get(reverse("jobs:delete", kwargs={"pk": job.id}))

        self.assertFalse(Job.objects.filter(id=job.id).exists())
        self.assertFalse(PeriodicTask.objects.filter(name=job.id).exists())

    def test_run_history(self):
        job = baker.make("jobs.Job", name="test job", owner=self.user)
        job_run = baker.make("jobs.JobRun", job=job, status="SUCCEEDED")

        response = self.client.get(reverse("jobs:run_history", kwargs={"pk": job.id}), follow=True)

        self.assertQuerysetEqual(job.get_job_run_history(), [job_run], transform=lambda x: x)
        self.assertContains(response, "Succeeded")

    def test_no_run_history(self):
        """If the job has no runs, an appropriate message should be displayed."""
        job = baker.make("jobs.Job", name="test job", owner=self.user)
        response = self.client.get(reverse("jobs:run_history", kwargs={"pk": job.id}), follow=True)

        self.assertIsNone(job.get_job_run_history())
        self.assertContains(response, "No run history.")

    def test_update_task_form(self):
        """When updating a periodic job, the task form should be initialized with the existing task parameters."""
        self.client.post(reverse("jobs:create"), self.periodic_form_data)
        job = Job.objects.get(name="periodic job")

        response = self.client.get(reverse("jobs:update_task_form"), {"job_id": job.id, "task_name": "REFRESH_DATA"})

        self.assertEqual(response.context["task_form"].initial["dataset_key"], "test key")
