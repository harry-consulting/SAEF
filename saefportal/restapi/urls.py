from django.urls import path, include
from rest_framework.routers import SimpleRouter

from restapi import views

router = SimpleRouter()
router.register(r"organization-groups", views.OrganizationGroupViewSet)
router.register(r"object-permissions", views.ObjectPermissionViewSet)
router.register(r"connections", views.ConnectionViewSet)
router.register(r"postgres-datastores", views.PostgresDatastoreViewSet)
router.register(r"azure-datastores", views.AzureDatastoreViewSet)
router.register(r"one-drive-datastores", views.OneDriveDatastoreViewSet)
router.register(r"google-drive-datastores", views.GoogleDriveDatastoreViewSet)
router.register(r"dropbox-datastores", views.DropboxDatastoreViewSet)
router.register(r"google-cloud-storage-datastores", views.GoogleCloudStorageDatastoreViewSet)
router.register(r"azure-blob-storage-datastores", views.AzureBlobStorageDatastoreViewSet)
router.register(r"azure-data-lake-datastores", views.AzureDataLakeDatastoreViewSet)
router.register(r"amazon-s3-datastores", views.AmazonS3DatastoreViewSet)
router.register(r"datasets", views.DatasetViewSet)
router.register(r"dataset-runs", views.DatasetRunViewSet)
router.register(r"notes", views.NoteViewSet)
router.register(r"jobs", views.JobViewSet)
router.register(r"job-runs", views.JobRunViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"contacts", views.ContactViewSet)
router.register(r"one-drive-datalakes", views.OneDriveDatalakeViewSet)
router.register(r"google-drive-datalakes", views.GoogleDriveDatalakeViewSet)
router.register(r"dropbox-datalakes", views.DropboxDatalakeViewSet)
router.register(r"google-cloud-storage-datalakes", views.GoogleCloudStorageDatalakeViewSet)
router.register(r"azure-blob-storage-datalakes", views.AzureBlobStorageDatalakeViewset)
router.register(r"azure-data-lake-datalakes", views.AzureDataLakeDatalakeViewset)
router.register(r"amazon-s3-datalakes", views.AmazonS3DatalakeViewset)
router.register(r"local-datalakes", views.LocalDatalakeViewset)


urlpatterns = [
    path('', views.APIRoot.as_view(), name="api-root"),
    path('', include(router.urls)),
    path('organizations/<int:pk>/', views.OrganizationInstance.as_view(), name='organization-detail'),
    path('settings/<int:pk>/', views.SettingsInstance.as_view(), name='settings-detail'),
    path('profile-dataset/', views.ProfileDataset.as_view(), name='profile-dataset'),
    path('refresh-data/', views.RefreshData.as_view(), name='refresh-data'),
    path('extract-metadata/', views.ExtractMetadata.as_view(), name='extract-metadata'),
    path('read-data/', views.ReadData.as_view(), name='read-data'),
]
