import io

from azure.storage.blob import BlobServiceClient
from django.db import models
from fernet_fields import EncryptedCharField

from datastores.models.file_datastore import FileDatastore
from datastores.util import get_viable_blob_datasets


class AzureBlobStorageDatastore(FileDatastore):
    storage_account_name = models.CharField(max_length=100)
    container_name = models.CharField(max_length=200)
    connection_string = EncryptedCharField(max_length=256)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the storage account name.
        if not self.pk:
            self.storage_account_name = self.connection_string.split(";")[1].replace("AccountName=", "")

        super(AzureBlobStorageDatastore, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = blob_service_client.get_container_client(container=self.container_name)

    def __str__(self):
        return f"{self.storage_account_name} (Azure Blob Storage)"

    def get_connection_details(self):
        return f"Connection string: {self.connection_string}, Blob container: {self.container_name}"

    def is_connection_valid(self):
        # If the connection string is valid (needed to initialize the object), we assume the connection is valid.
        return True

    def get_viable_datasets(self):
        return get_viable_blob_datasets(self.container_client.list_blobs(), "name")

    def _download_data(self, file_id):
        data = io.BytesIO(self.container_client.download_blob(file_id).readall())
        file_type = file_id.split(".")[-1]

        return data, file_type
