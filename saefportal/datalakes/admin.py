from django.contrib import admin

from datalakes.models import (OneDriveDatalake, GoogleDriveDatalake, DropboxDatalake, GoogleCloudStorageDatalake,
                              AzureBlobStorageDatalake, AmazonS3Datalake, LocalDatalake)

admin.site.register(OneDriveDatalake)
admin.site.register(GoogleDriveDatalake)
admin.site.register(DropboxDatalake)
admin.site.register(GoogleCloudStorageDatalake)
admin.site.register(AzureBlobStorageDatalake)
admin.site.register(AmazonS3Datalake)
admin.site.register(LocalDatalake)
