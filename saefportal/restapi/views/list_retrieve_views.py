from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet

import datastores.models
import datalakes.models
from datasets.models import Connection, Dataset, DatasetRun, Note
from jobs.models import Job, JobRun
from restapi import serializers
from restapi.mixins import FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin
from settings.models import Contact, Settings
from users.models import User, Organization, OrganizationGroup, ObjectPermission


class OrganizationInstance(BasicLoggingMixin, RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class OrganizationGroupViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = OrganizationGroup.objects.all().order_by("id")
    serializer_class = serializers.OrganizationGroupSerializer


class ObjectPermissionViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = ObjectPermission.objects.all().order_by("id")
    serializer_class = serializers.ObjectPermissionSerializer


class ConnectionViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = serializers.ConnectionSerializer
    object_permission = "view_connection"


class PostgresDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.PostgresDatastore.objects.all()
    serializer_class = serializers.PostgresDatastoreSerializer
    object_permission = "view_connection"


class AzureDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.AzureDatastore.objects.all()
    serializer_class = serializers.AzureDatastoreSerializer
    object_permission = "view_connection"


class OneDriveDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.OneDriveDatastore.objects.all()
    serializer_class = serializers.OneDriveDatastoreSerializer
    object_permission = "view_connection"


class GoogleDriveDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.GoogleDriveDatastore.objects.all()
    serializer_class = serializers.GoogleDriveDatastoreSerializer
    object_permission = "view_connection"


class DropboxDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.DropboxDatastore.objects.all()
    serializer_class = serializers.DropboxDatastoreSerializer
    object_permission = "view_connection"


class GoogleCloudStorageDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.GoogleCloudStorageDatastore.objects.all()
    serializer_class = serializers.GoogleCloudStorageDatastoreSerializer
    object_permission = "view_connection"


class AzureBlobStorageDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.AzureBlobStorageDatastore.objects.all()
    serializer_class = serializers.AzureBlobStorageDatastoreSerializer
    object_permission = "view_connection"


class AzureDataLakeDatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.AzureDataLakeDatastore.objects.all()
    serializer_class = serializers.AzureDataLakeDatastoreSerializer
    object_permission = "view_connection"


class AmazonS3DatastoreViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datastores.models.AmazonS3Datastore.objects.all()
    serializer_class = serializers.AmazonS3DatastoreSerializer
    object_permission = "view_connection"


class DatasetViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    object_permission = "view_dataset"


class DatasetRunViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = DatasetRun.objects.all()
    serializer_class = serializers.DatasetRunSerializer
    object_permission = "view_dataset"


class NoteViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    object_permission = "view_dataset"


class JobViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = serializers.JobSerializer
    object_permission = "view_job"


class JobRunViewSet(FilterQuerysetByObjectPermissionMixin, BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = JobRun.objects.all()
    serializer_class = serializers.JobRunSerializer
    object_permission = "view_job"


class UserViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminUser]


class ContactViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = Contact.objects.all().order_by("id")
    serializer_class = serializers.ContactSerializer


class SettingsInstance(BasicLoggingMixin, RetrieveAPIView):
    queryset = Settings.objects.all()
    serializer_class = serializers.SettingsSerializer


class OneDriveDatalakeViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.OneDriveDatalake.objects.all().order_by("id")
    serializer_class = serializers.OneDriveDatalakeSerializer


class GoogleDriveDatalakeViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.GoogleDriveDatalake.objects.all().order_by("id")
    serializer_class = serializers.GoogleDriveDatalakeSerializer


class DropboxDatalakeViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.DropboxDatalake.objects.all().order_by("id")
    serializer_class = serializers.DropboxDatalakeSerializer


class GoogleCloudStorageDatalakeViewSet(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.GoogleCloudStorageDatalake.objects.all().order_by("id")
    serializer_class = serializers.GoogleCloudStorageDatalakeSerializer


class AzureBlobStorageDatalakeViewset(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.AzureBlobStorageDatalake.objects.all().order_by("id")
    serializer_class = serializers.AzureBlobStorageDatalakeSerializer


class AzureDataLakeDatalakeViewset(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.AzureDataLakeDatalake.objects.all().order_by("id")
    serializer_class = serializers.AzureDataLakeDatalakeSerializer


class AmazonS3DatalakeViewset(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.AmazonS3Datalake.objects.all().order_by("id")
    serializer_class = serializers.AmazonS3DatalakeSerializer


class LocalDatalakeViewset(BasicLoggingMixin, ReadOnlyModelViewSet):
    queryset = datalakes.models.LocalDatalake.objects.all().order_by("id")
    serializer_class = serializers.LocalDatalakeSerializer
