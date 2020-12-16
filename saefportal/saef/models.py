from __future__ import absolute_import, unicode_literals
from django.utils import timezone
from .enums import MonitorStatus, SessionStatus, SessionProgress, DatasetType, DatasetAccess

from django.db import models
import uuid


class ConnectionType(models.Model):
    name = models.CharField(max_length=128)
    version = models.CharField(max_length=32, default="Latest")

    def __str__(self):
        return self.name


class Connection(models.Model):
    name = models.CharField(max_length=128)
    time_out = models.IntegerField(default=120)
    connection_type = models.ForeignKey(ConnectionType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class PostgresConnection(models.Model):
    db_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=300)
    port = models.IntegerField(default=5432)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=True, null=True)


class AzureConnection(models.Model):
    db_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=300)
    port = models.IntegerField(default=1433)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=True, null=True)


class AzureBlobStorageConnection(models.Model):
    connection_string = models.CharField(max_length=1000)
    container_name = models.CharField(max_length=500)
    blob_name = models.CharField(max_length=500)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=True, null=True)


class ApplicationToken(models.Model):
    application_token = models.UUIDField(editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=128, default='Unknown')
    business_owner = models.CharField(max_length=256)
    application_group_name = models.CharField(max_length=128)
    created_by = models.CharField(max_length=256)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + '_' + str(self.application_token) + '_' + str(self.pk)


class Application(models.Model):
    application_token = models.ForeignKey(ApplicationToken, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    application_key = models.UUIDField(editable=False, default=uuid.uuid4)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ApplicationSession(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    execution_id = models.UUIDField(editable=False, default=uuid.uuid4)

    status_time = models.DateTimeField(blank=True, null=True)
    status_type = models.CharField(max_length=128, choices=SessionStatus.choices())


class ApplicationSessionMetaData(models.Model):
    application_session = models.ForeignKey(ApplicationSession, on_delete=models.CASCADE)
    actual_execution_time = models.DurationField()
    expected_execution_time = models.DurationField()

    status_type = models.CharField(max_length=128, choices=MonitorStatus.choices())

    def get_status_label(self):
        return MonitorStatus.format(self.status_type)

    def session_created(self):
        return self.application_session.create_timestamp

    def session_ended(self):
        return self.application_session.create_timestamp + self.actual_execution_time

    def session_name(self):
        return f"{self.application_session.application}_{self.pk}"


class Job(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class JobSession(models.Model):
    application_session = models.ForeignKey(ApplicationSession, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    execution_id = models.UUIDField(editable=False, default=uuid.uuid4)

    status_time = models.DateTimeField(blank=True, null=True)
    status_type = models.CharField(max_length=128, choices=SessionStatus.choices(), default=SessionStatus.START)


class JobSessionMetaData(models.Model):
    job_session = models.ForeignKey(JobSession, on_delete=models.CASCADE)
    actual_execution_time = models.DurationField()
    expected_execution_time = models.DurationField()

    status_type = models.CharField(max_length=128, choices=MonitorStatus.choices())

    def get_status_label(self):
        return MonitorStatus.format(self.status_type)

    def session_created(self):
        return self.job_session.create_timestamp

    def session_ended(self):
        return self.job_session.create_timestamp + self.actual_execution_time

    def session_name(self):
        return f"{self.job_session.job}_{self.pk}"


class JobSessionStatus(models.Model):
    job_session = models.ForeignKey(JobSession, on_delete=models.CASCADE)

    status_type = models.CharField(max_length=64, choices=SessionProgress.choices(), default=SessionProgress.START)
    description = models.CharField(max_length=2048, null=True)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('create_timestamp',)

    def __str__(self):
        return str(self.job_session) + '_' + str(self.status_type)


class Dataset(models.Model):
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    sequence_in_job = models.IntegerField(default=1)
    dataset_key = models.CharField(max_length=128, blank=True, unique=True, default=uuid.uuid4)
    dataset_name = models.CharField(max_length=128)

    dataset_type = models.CharField(max_length=32, choices=DatasetType.choices(), default=DatasetType.INPUT)

    query_timeout = models.IntegerField(default=300)
    dataset_access_method = models.CharField(max_length=32, choices=DatasetAccess.choices(),
                                             default=DatasetAccess.TABLE.value)
    dataset_extraction_sql = models.CharField(max_length=5000, null=True, blank=True, default=None)
    dataset_extraction_table = models.CharField(max_length=5000, null=True, blank=True)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.dataset_name


class DatasetSession(models.Model):
    job_session = models.ForeignKey(JobSession, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    status_time = models.DateTimeField(blank=True, null=True)
    execution_id = models.UUIDField(editable=False, default=uuid.uuid4)
    degree_of_change = models.FloatField(null=True)


class DatasetSessionMetaData(models.Model):
    dataset_session = models.ForeignKey(DatasetSession, on_delete=models.CASCADE)
    status_type = models.CharField(max_length=128, choices=MonitorStatus.choices())

    def get_status_label(self):
        return MonitorStatus.format(self.status_type)

    def session_created(self):
        return self.dataset_session.create_timestamp

    def session_ended(self):
        return self.dataset_session.create_timestamp + timezone.timedelta(hours=1)

    def session_name(self):
        return f"{self.dataset_session.dataset}_{self.pk}"


class DatasetMetadataColumn(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=512)
    data_type = models.CharField(max_length=128)
    is_null = models.BooleanField()
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.column_name


class DatasetMetadataConstraint(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    constraint_name = models.CharField(max_length=128, default='')
    columns = models.CharField(max_length=1024)
    constraint_type = models.CharField(max_length=128)
    constraint_definition = models.CharField(max_length=5000)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.constraint_name


class DatasetProfileHistory(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    job_session = models.ForeignKey(JobSession, on_delete=models.CASCADE, null=True)
    profile_json = models.CharField(max_length=5000)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('dataset', 'job_session', 'create_timestamp',)

    def __str__(self):
        return str(self.dataset) + str(self.job_session)


class ColumnProfileHistory(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    column = models.ForeignKey(DatasetMetadataColumn, on_delete=models.CASCADE, null=True)
    job_session = models.ForeignKey(JobSession, on_delete=models.CASCADE, null=True)
    column_name = models.CharField(max_length=1024)
    profile_json = models.CharField(max_length=5000)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('dataset', 'job_session', 'create_timestamp',)

    def __str__(self):
        return self.column_name + str(self.job_session)


class DatasetProfileOperationHistory(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    update_mode = models.CharField(max_length=16)
    batch_id = models.BigIntegerField()
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.batch_id) + self.dataset
