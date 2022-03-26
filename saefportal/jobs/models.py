import uuid

from cron_descriptor import get_description
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask
from simple_history.models import HistoricalRecords

from saef.mixins import SaveWithoutHistoricalRecordMixin
from users.models import User


class Job(models.Model, SaveWithoutHistoricalRecordMixin):
    class TemplateTask(models.TextChoices):
        PROFILE_DATASET = "PROFILE_DATASET", _("Profile dataset")
        REFRESH_DATA = "REFRESH_DATA", _("Refresh data")
        EXTRACT_METADATA = "EXTRACT_METADATA", _("Extract metadata")

    name = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, default="")
    template_task = models.CharField(max_length=64, choices=TemplateTask.choices)

    alert_on_start_email = models.CharField("On start", max_length=500, blank=True, null=True)
    alert_on_success_email = models.CharField("On success", max_length=500, blank=True, null=True)
    alert_on_failure_email = models.CharField("On failure", max_length=500, blank=True, null=True)

    history = HistoricalRecords(excluded_fields=["owner", "description", "template_task", "alert_on_start_email",
                                                 "alert_on_success_email", "alert_on_failure_email"])

    def __str__(self):
        return self.name

    def get_task(self):
        """Return a three-tuple with the format (task_type, task, task_label)."""
        return "template", self.template_task, self.TemplateTask[self.template_task].label

    def get_readable_cron(self):
        """If the job is scheduled, return the cron syntax and a human readable version of the cron syntax."""
        periodic_task = self.get_periodic_task()
        if periodic_task:
            crontab_lst = str(periodic_task.crontab).split(" ")
            crontab = " ".join(crontab_lst[:len(crontab_lst)-2])

            return crontab, get_description(crontab)
        else:
            return "", "Manual"

    def get_periodic_task(self):
        try:
            return PeriodicTask.objects.get(name=self.id)
        except PeriodicTask.DoesNotExist:
            return None

    def has_email_alerts(self):
        return (self.alert_on_start_email or self.alert_on_success_email or self.alert_on_failure_email) is not None

    def get_last_job_run(self):
        job_history = JobRun.objects.filter(job=self).order_by("-start_datetime")
        if job_history:
            return job_history[0]
        else:
            return None

    def get_job_run_history(self):
        job_history = JobRun.objects.filter(job=self).order_by("-start_datetime")
        if job_history:
            return job_history
        else:
            return None


class JobRun(models.Model):
    class Status(models.TextChoices):
        SUCCEEDED = "SUCCEEDED", _("Succeeded")
        SUCCEEDED_ISSUE = "SUCCEEDED_ISSUE", _("Succeeded with issue")
        FAILED = "FAILED", _("Failed")
        RUNNING = "RUNNING", _("Running")

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_runs")
    start_datetime = models.DateTimeField("Run Start Time", auto_now_add=True)
    end_datetime = models.DateTimeField("Run End Time", blank=True, null=True)
    execution_id = models.UUIDField(editable=False, default=uuid.uuid4)

    status = models.CharField(max_length=64, choices=Status.choices, default=Status.RUNNING)
    result = models.JSONField(blank=True, null=True)
    parameters = models.JSONField(blank=True, null=True)

    def get_status_icon(self):
        if self.status == self.Status.SUCCEEDED:
            return '<i class="fas fa-check-circle success-green"></i>'
        elif self.status == self.Status.SUCCEEDED_ISSUE:
            return '<i class="fas fa-check-circle success-with-issue-yellow"></i>'
        elif self.status == self.Status.RUNNING:
            return '<i class="fas fa-sync-alt"></i>'
        else:
            return '<i class="fas fa-exclamation-circle warning-red"></i>'
