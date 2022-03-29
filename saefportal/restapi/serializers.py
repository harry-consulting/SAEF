import json

from rest_framework import serializers
from rest_framework.reverse import reverse

import datastores.models
import datalakes.models
from datasets.models import Connection, Dataset, DatasetRun, Note
from jobs.models import Job, JobRun
from settings.models import Contact, Settings
from users.models import User, Organization, OrganizationGroup, ObjectPermission


class ConnectionSerializer(serializers.HyperlinkedModelSerializer):
    datastore = serializers.SerializerMethodField("get_datastore")

    class Meta:
        model = Connection
        fields = ["url", "id", "name", "owner", "type", "key", "datastore", "datasets"]

    def get_datastore(self, connection):
        request = self.context["request"]

        datastore_type = connection.type.replace("_", "").lower()
        return reverse(f"{datastore_type}datastore-detail", request=request, args=[connection.datastore.id])


class PostgresDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.PostgresDatastore
        fields = ["url", "id", "database_name", "username", "host", "port"]


class AzureDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.AzureDatastore
        fields = ["url", "id", "database_name", "username", "host", "port"]


class OneDriveDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.OneDriveDatastore
        fields = ["username", "root_path"]


class GoogleDriveDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.GoogleDriveDatastore
        fields = ["username", "root_path"]


class DropboxDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.DropboxDatastore
        fields = ["username", "root_path"]


class GoogleCloudStorageDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.GoogleCloudStorageDatastore
        fields = ["username", "project_id", "bucket_name"]


class AzureBlobStorageDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.AzureBlobStorageDatastore
        fields = ["storage_account_name", "container_name"]


class AzureDataLakeDatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.AzureDataLakeDatastore
        fields = ["storage_account_name", "container_name"]


class AmazonS3DatastoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datastores.models.AmazonS3Datastore
        fields = ["username", "bucket_name"]


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    notes = serializers.HyperlinkedRelatedField(many=True, view_name="note-detail", read_only=True)

    class Meta:
        model = Dataset
        fields = ["url", "id", "name", "owner", "description", "tags", "contacts", "connection", "query",
                  "table", "type", "key", "create_datetime", "dataset_runs", "notes"]


class DatasetRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DatasetRun
        fields = ["url", "id", "dataset", "start_datetime", "end_datetime", "execution_id", "task_name", "result",
                  "status"]


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ["url", "id", "dataset", "text", "created_by", "updated_at"]


class JobSerializer(serializers.HyperlinkedModelSerializer):
    task = serializers.SerializerMethodField("get_task")
    schedule_crontab = serializers.SerializerMethodField("get_schedule_crontab")
    schedule_start_time = serializers.SerializerMethodField("get_schedule_start_time")
    schedule_arguments = serializers.SerializerMethodField("get_schedule_arguments")

    class Meta:
        model = Job
        fields = ["url", "id", "name", "owner", "task", "schedule_crontab", "schedule_start_time", "schedule_arguments",
                  "alert_on_start_email", "alert_on_success_email", "alert_on_failure_email", "job_runs"]

    def get_task(self, job):
        return job.get_task()[2]

    def get_schedule_crontab(self, job):
        periodic_task = job.get_periodic_task()

        if periodic_task:
            crontab_lst = str(periodic_task.crontab).split(" ")
            return " ".join(crontab_lst[:len(crontab_lst)-2])
        else:
            return None

    def get_schedule_start_time(self, job):
        periodic_task = job.get_periodic_task()
        return periodic_task.start_time if periodic_task is not None else None

    def get_schedule_arguments(self, job):
        periodic_task = job.get_periodic_task()
        return json.loads(periodic_task.kwargs)["task_parameters"] if periodic_task is not None else None


class JobRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobRun
        fields = ["url", "id", "job", "start_datetime", "end_datetime", "execution_id", "status", "result",
                  "parameters"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    first_name = serializers.ReadOnlyField(source="user_profile.first_name")
    last_name = serializers.ReadOnlyField(source="user_profile.last_name")
    phone = serializers.ReadOnlyField(source="user_profile.phone")

    class Meta:
        model = User
        fields = ["url", "id", "email", "date_joined", "is_active", "is_staff", "is_superuser", "first_name",
                  "last_name", "phone", "organization_groups", "object_permissions"]


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contact
        fields = ["url", "id", "name", "email"]


class SettingsSerializer(serializers.HyperlinkedModelSerializer):
    datalake = serializers.SerializerMethodField("get_datalake")

    class Meta:
        model = Settings
        fields = ["url", "id", "timezone", "datalake", "dataset_refresh_frequency", "try_live_connection",
                  "profile_expected_datasets_n", "profile_failed_threshold", "profile_delta_deviation",
                  "email_host_user", "email_host", "email_port", "email_use_tls"]

    def get_datalake(self, settings):
        request = self.context["request"]
        datalake_class = settings.datalake.__class__.__name__.lower()

        return reverse(f"{datalake_class}-detail", request=request, args=[settings.datalake.id])


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "settings"]


class OrganizationGroupSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.SerializerMethodField("get_users")

    class Meta:
        model = OrganizationGroup
        fields = ["name", "parent", "object_permissions", "users"]

    def get_users(self, group):
        request = self.context["request"]

        return [reverse("user-detail", [user.id], request=request)
                for user in User.objects.filter(organization_groups=group)]


class ObjectPermissionSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.SerializerMethodField("get_content_type")

    class Meta:
        model = ObjectPermission
        fields = ["can_view", "can_update", "can_delete", "can_execute", "content_type", "object_id"]

    def get_content_type(self, permission):
        return str(permission.content_type)


class OneDriveDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.OneDriveDatalake
        fields = ["username", "root_path"]


class GoogleDriveDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.GoogleDriveDatalake
        fields = ["username", "root_path"]


class DropboxDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.DropboxDatalake
        fields = ["username", "root_path"]


class GoogleCloudStorageDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.GoogleCloudStorageDatalake
        fields = ["username", "project_id"]


class AzureBlobStorageDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.AzureBlobStorageDatalake
        fields = ["storage_account_name", "container_name"]


class AzureDataLakeDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.AzureDataLakeDatalake
        fields = ["storage_account_name", "container_name"]


class AmazonS3DatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.AmazonS3Datalake
        fields = ["username", "bucket_name"]


class LocalDatalakeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = datalakes.models.LocalDatalake
        fields = ["root_path"]


class ProfileDatasetSerializer(serializers.Serializer):
    dataset_key = serializers.CharField(max_length=100)


class RefreshDataSerializer(serializers.Serializer):
    dataset_key = serializers.CharField(max_length=100)
    degree_of_change_threshold = serializers.FloatField(min_value=0, max_value=1, required=False)


class ExtractMetadataSerializer(serializers.Serializer):
    dataset_key = serializers.CharField(max_length=100)


class ReadDataSerializer(serializers.Serializer):
    dataset_key = serializers.CharField(max_length=100)
    sql_query = serializers.CharField(max_length=500, required=False)
