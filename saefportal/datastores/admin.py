from django.contrib import admin

from datastores.models import (PostgresDatastore, AzureDatastore, OneDriveDatastore, GoogleDriveDatastore,
                               DropboxDatastore, GoogleCloudStorageDatastore, AzureBlobStorageDatastore,
                               AmazonS3Datastore)

admin.site.register(PostgresDatastore)
admin.site.register(AzureDatastore)
admin.site.register(OneDriveDatastore)
admin.site.register(GoogleDriveDatastore)
admin.site.register(DropboxDatastore)
admin.site.register(GoogleCloudStorageDatastore)
admin.site.register(AzureBlobStorageDatastore)
admin.site.register(AmazonS3Datastore)
