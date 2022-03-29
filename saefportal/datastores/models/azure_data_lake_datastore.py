import io

from azure.storage.filedatalake import DataLakeServiceClient
from django.db import models
from fernet_fields import EncryptedCharField

from datastores.models.file_datastore import FileDatastore
from datastores.util import get_viable_blob_datasets


class AzureDataLakeDatastore(FileDatastore):
    storage_account_name = models.CharField(max_length=100)
    container_name = models.CharField(max_length=200)
    connection_string = EncryptedCharField(max_length=256)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the storage account name.
        if not self.pk:
            self.storage_account_name = self.connection_string.split(";")[1].replace("AccountName=", "")

        super(AzureDataLakeDatastore, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)
        self.file_system_client = datalake_service_client.get_file_system_client(self.container_name)

    def __str__(self):
        return f"{self.storage_account_name} (Azure Data Lake)"

    def get_connection_details(self):
        return f"Connection string: {self.connection_string}, Blob container: {self.container_name}"

    def is_connection_valid(self):
        # If the connection string is valid (needed to initialize the object), we assume the connection is valid.
        return True

    def get_viable_datasets(self):
        return get_viable_blob_datasets(self.file_system_client.get_paths(), "name")

    def _download_data(self, file_id):
        file_client = self.file_system_client.get_file_client(file_id)

        data = io.BytesIO(file_client.download_file().readall())
        file_type = file_id.split(".")[-1]

        return data, file_type
