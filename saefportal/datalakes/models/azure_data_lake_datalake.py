import io
import json
import logging
import uuid

import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
from django.db import models
from fernet_fields import EncryptedCharField

from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class AzureDataLakeDatalake(models.Model):
    storage_account_name = models.CharField(max_length=100)
    container_name = models.CharField(max_length=200)
    connection_string = EncryptedCharField(max_length=256)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the storage account name and, if necessary, create a blob container.
        if not self.pk:
            self.storage_account_name = self.connection_string.split(";")[1].replace("AccountName=", "")

            if self.container_name not in [fs.name for fs in self.datalake_service_client.list_file_systems()]:
                new_container_name = self.container_name if self.container_name else f"saef-{uuid.uuid4()}"
                self.datalake_service_client.create_file_system(file_system=new_container_name)
                self.container_name = new_container_name

                logger.info(f"Created new container '{new_container_name}' in {self}.")

        super(AzureDataLakeDatalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

    def __str__(self):
        return f"{self.storage_account_name} (Azure Data Lake)"

    def list_objects(self, path):
        file_system_client = self.datalake_service_client.get_file_system_client(self.container_name)

        return [path.name.split("/")[-1] for path in file_system_client.get_paths(path=path)]

    def create_folder(self, path, folder_name):
        full_path = f"{path}/{folder_name}" if path else f"{folder_name}"
        file_system_client = self.datalake_service_client.get_file_system_client(self.container_name)

        file_system_client.create_directory(directory=full_path)
        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        file_system_client = self.datalake_service_client.get_file_system_client(self.container_name)

        # Note that this also works on files despite the method name.
        file_system_client.delete_directory(directory=path)
        logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        file_system_client = self.datalake_service_client.get_file_system_client(self.container_name)
        directory_client = file_system_client.get_directory_client(path)

        file_client = directory_client.get_file_client(filename)

        file_client.upload_data(content, overwrite=True)
        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

    def download_file(self, path, query="latest"):
        file_system_client = self.datalake_service_client.get_file_system_client(self.container_name)
        directory_client = file_system_client.get_directory_client(path)

        filename, timestamp = get_wanted_file(query, self.list_objects(path))

        file_client = directory_client.get_file_client(filename)
        raw_data = file_client.download_file().readall()
        data = pd.read_parquet(io.BytesIO(raw_data)) if filename.split(".")[-1] == "parquet" else json.loads(raw_data)

        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
