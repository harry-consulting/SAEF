import io
import json
import logging
import uuid

import pandas as pd
from azure.storage.blob import BlobServiceClient, ContentSettings
from django.db import models
from fernet_fields import EncryptedCharField

from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class AzureBlobStorageDatalake(models.Model):
    storage_account_name = models.CharField(max_length=100)
    container_name = models.CharField(max_length=200)
    connection_string = EncryptedCharField(max_length=256)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the storage account name and, if necessary, create a blob container.
        if not self.pk:
            self.storage_account_name = self.connection_string.split(";")[1].replace("AccountName=", "")

            if self.container_name not in [c["name"] for c in self.blob_service_client.list_containers()]:
                new_container_name = self.container_name if self.container_name else f"saef-{uuid.uuid4()}"
                self.blob_service_client.create_container(new_container_name)
                self.container_name = new_container_name

                logger.info(f"Created new container '{new_container_name}' in {self}.")

        super(AzureBlobStorageDatalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

    def __str__(self):
        return f"{self.storage_account_name} (Azure Blob Storage)"

    def list_objects(self, path):
        container_client = self.blob_service_client.get_container_client(container=self.container_name)

        filenames = [blob["name"].split("/")[-1] for blob in container_client.list_blobs(name_starts_with=path)]
        return [filename for filename in filenames if filename != "keep.txt"]

    def create_folder(self, path, folder_name):
        full_path = f"{path}/{folder_name}/keep.txt" if path else f"{folder_name}/keep.txt"

        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=full_path)

        blob_client.upload_blob("")
        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        container_client = self.blob_service_client.get_container_client(container=self.container_name)

        for blob in container_client.list_blobs(name_starts_with=path):
            container_client.delete_blob(blob)

        logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=f"{path}/{filename}")

        content_type = "application/octet-stream" if filename.split(".")[-1] == "parquet" else "application/json"

        blob_client.upload_blob(content, content_settings=ContentSettings(content_type=content_type))
        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

    def download_file(self, path, query="latest"):
        container_client = self.blob_service_client.get_container_client(container=self.container_name)

        filename, timestamp = get_wanted_file(query, self.list_objects(path))

        raw_data = container_client.download_blob(f"{path}/{filename}").readall()
        data = pd.read_parquet(io.BytesIO(raw_data)) if filename.split(".")[-1] == "parquet" else json.loads(raw_data)

        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
