import json
import uuid
from datetime import datetime

from django.core.validators import RegexValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from analyzer.models import ActualDatasetProfile, ExpectedDatasetProfile, ActualColumnProfile, ExpectedColumnProfile
from jobs.models import Job
from saef.mixins import SaveWithoutHistoricalRecordMixin
from settings.models import Contact
from users.models import User

filename_validator = RegexValidator(r"^[\w\-. ]+$", "Name cannot be used as a folder name in the datalake.")


class Connection(models.Model):
    class Type(models.TextChoices):
        POSTGRES = "POSTGRES", _("PostgreSQL")
        AZURE = "AZURE", _("Azure SQL")
        ONEDRIVE = "ONEDRIVE", _("OneDrive")
        GOOGLE_DRIVE = "GOOGLE_DRIVE", _("Google Drive")
        DROPBOX = "DROPBOX", _("Dropbox")
        GOOGLE_CLOUD_STORAGE = "GOOGLE_CLOUD_STORAGE", _("Google Cloud Storage")
        AZURE_BLOB_STORAGE = "AZURE_BLOB_STORAGE", _("Azure Blob Storage")
        AZURE_DATA_LAKE = "AZURE_DATA_LAKE", _("Azure Data Lake")
        AMAZON_S3 = "AMAZON_S3", _("Amazon S3")

    name = models.CharField(max_length=128, unique=True, validators=[filename_validator])
    title = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=128, choices=Type.choices)
    key = models.UUIDField(editable=False, default=uuid.uuid4)

    datastore_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    datastore_id = models.PositiveIntegerField(blank=True, null=True)
    datastore = GenericForeignKey("datastore_type", "datastore_id")

    history = HistoricalRecords(excluded_fields=["owner", "type", "key", "datastore_type", "datastore_id",
                                                 "datastore", "title"])

    def save(self, *args, **kwargs):
        # If the object has not been created yet.
        if not self.pk:
            self.title = self.name

        super(Connection, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_related_datasets(self):
        """Return a dict with related datasets under the categories "TABLE", "QUERY" and "VIEW"."""
        related_datasets = Dataset.objects.filter(connection_id=self.id)

        structure = {Dataset.Type.TABLE: [], Dataset.Type.QUERY: [], Dataset.Type.VIEW: []}
        [structure[dataset.type].append(dataset) for dataset in related_datasets]

        # Order the lists alphabetically.
        for key, values in structure.items():
            structure[key] = sorted(values, key=lambda x: x.name)

        return structure


class Dataset(models.Model, SaveWithoutHistoricalRecordMixin):
    class Type(models.TextChoices):
        QUERY = "QUERY", _("Query")
        TABLE = "TABLE", _("Table")
        VIEW = "VIEW", _("View")

    name = models.CharField(max_length=128, validators=[filename_validator])
    title = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, default="")
    tags = models.CharField(max_length=1024, blank=True, default="")
    contacts = models.ManyToManyField(Contact, blank=True)

    # If null, the dataset is a manually uploaded file.
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="datasets", blank=True, null=True)

    query = models.CharField(max_length=5000, null=True, blank=True)
    table = models.CharField(max_length=500, null=True, blank=True)
    file_id = models.CharField(max_length=500, null=True, blank=True)
    type = models.CharField(max_length=128, choices=Type.choices, default=Type.QUERY)

    key = models.UUIDField(editable=False, default=uuid.uuid4)
    create_datetime = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords(excluded_fields=["description", "tags", "contacts", "connection", "query", "table",
                                                 "file_id", "type", "key", "create_datetime", "test", "owner", "title"])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "connection"], name="Name uniqueness")]

    def save(self, *args, **kwargs):
        # If the object has not been created yet.
        if not self.pk:
            self.title = self.name

        super(Dataset, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_status(self):
        """Return the status of the latest related dataset session."""
        latest_session = DatasetRun.objects.filter(dataset_id=self.id).order_by("start_datetime")

        if latest_session:
            from django.utils import formats
            status_datetime = formats.date_format(latest_session[0].start_datetime, "DATETIME_FORMAT")
            return f"{latest_session[0].get_status_icon()} {latest_session[0].get_status_display()}: {status_datetime}"
        else:
            return "No status."

    def get_linked_jobs(self):
        """
        Return a list of job objects that are linked to the dataset. A job is linked to a dataset if the job currently
        uses the dataset key in its parameters.
        """
        linked_jobs = []
        jobs = Job.objects.all()

        for job in jobs:
            parameters = None

            periodic_task = job.get_periodic_task()
            if periodic_task:
                parameters = json.loads(periodic_task.kwargs)["task_parameters"]
            elif job.get_last_job_run():
                parameters = job.get_last_job_run().parameters

            if parameters is not None and parameters.get("dataset_key", None) == str(self.key):
                linked_jobs.append(job)

        return linked_jobs

    def get_notes(self):
        return Note.objects.filter(dataset=self).order_by("-updated_at")

    def get_profile_runs(self):
        return DatasetRun.objects.filter(dataset=self, task_name="Profile dataset").order_by("-start_datetime")

    def get_degree_of_change_data(self):
        """Return list data points that can be used to populate a line chart."""
        data = []

        for run in self.get_profile_runs().reverse():
            if run.result and "degree_of_change" in run.result:
                timestamp = int(run.start_datetime.strftime("%s")) * 1000
                degree_of_change = run.result["degree_of_change"]

                data.append({"x": timestamp, "y": degree_of_change, "id": run.id})

        return data

    def get_type_icon(self):
        if self.type == self.Type.QUERY:
            return '<i class="fas fa-search"></i>'
        elif self.type == self.Type.TABLE:
            return '<i class="fas fa-table"></i>'
        else:
            return '<i class="fas fa-eye"></i>'

    def get_connection_type_display(self):
        return self.connection.get_type_display() if self.connection else "Upload"

    def get_connection_details(self):
        return self.connection.datastore.get_connection_details() if self.connection else "No connection details"

    def get_datalake_path(self):
        """Return the path to the dataset in the datalake. If the datasets connection has been deleted, return None."""
        try:
            connection_folder = self.connection.name if self.connection else "uploads"
        except Connection.DoesNotExist:
            return None

        return f"saef/landing/{connection_folder}/{self.name}"


class DatasetRun(models.Model):
    class Type(models.TextChoices):
        JOB = "JOB", _("Job")
        API = "API", _("API")

    class Status(models.TextChoices):
        SUCCEEDED = "SUCCEEDED", _("Succeeded")
        SUCCEEDED_ISSUE = "SUCCEEDED_ISSUE", _("Succeeded with issue")
        FAILED = "FAILED", _("Failed")
        RUNNING = "RUNNING", _("Running")

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="dataset_runs")
    task_name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.JOB)

    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=100, default="")
    execution_id = models.UUIDField(editable=False, default=uuid.uuid4)

    result = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=128, choices=Status.choices, default=Status.RUNNING)

    def get_status_icon(self):
        if self.status == self.Status.SUCCEEDED:
            return '<i class="fas fa-check-circle success-green"></i>'
        elif self.status == self.Status.SUCCEEDED_ISSUE:
            return '<i class="fas fa-check-circle success-with-issue-yellow"></i>'
        elif self.status == self.Status.RUNNING:
            return '<i class="fas fa-sync-alt"></i>'
        else:
            return '<i class="fas fa-exclamation-circle warning-red"></i>'

    def get_actual_expected_dataset_profile(self):
        """Return dict with actual and expected data from the analyzers dataset profiles."""
        actual_dataset_profile = ActualDatasetProfile.objects.get(dataset_run=self)
        expected_dataset_profile = ExpectedDatasetProfile.objects.get(actual_dataset_profile=actual_dataset_profile)

        actual_expected_info = {}

        for key in ["row_count", "column_count", "hash_sum"]:
            actual_expected_info[key] = {"actual": getattr(actual_dataset_profile, key),
                                         "expected": getattr(expected_dataset_profile, key)}

        return actual_expected_info

    def get_actual_expected_column_profiles(self):
        """Return list of dicts with actual and expected data from the analyzers column profiles."""
        actual_expected_info = []
        actual_column_profiles = ActualColumnProfile.objects.filter(dataset_profile__dataset_run=self)

        for actual_column_profile in actual_column_profiles:
            actual_expected_column_info = {"name": actual_column_profile.name}
            expected_column_profile = ExpectedColumnProfile.objects.filter(
                dataset_profile__actual_dataset_profile__dataset_run=self, name=actual_column_profile.name).first()

            for key in ["min", "max", "uniqueness", "datatype", "nullable", "order", "hash_sum"]:
                actual = getattr(actual_column_profile, key)
                expected = getattr(expected_column_profile, key) if expected_column_profile else None

                # If the column is a date then format the actual and expected values to remove unnecessary information.
                try:
                    actual = datetime.strptime(actual[:-6], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                    expected = datetime.strptime(expected[:-6], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass

                actual_expected_column_info[key] = {"actual": actual, "expected": expected}

            actual_expected_info.append(actual_expected_column_info)

        return actual_expected_info


class Note(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="notes")
    text = models.TextField(max_length=2048)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
