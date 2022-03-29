import io
import json
import logging
import uuid

import pandas as pd
from django.db import models
from fernet_fields import EncryptedTextField

import util.google_util as util
from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class GoogleCloudStorageDatalake(models.Model):
    username = models.CharField(max_length=100)
    project_id = models.CharField(max_length=500)
    token_cache = EncryptedTextField()
    bucket_name = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        # If the object is not yet created, get the username and, if necessary, create a new bucket for the datalake.
        if not self.pk:
            service = util.get_service_from_cache(self, "cloud storage")
            self.username = service.get_service_account_email()

            if not self.bucket_name:
                bucket = service.create_bucket(bucket_or_name=f"saef-{uuid.uuid4()}", location="US-EAST1")
                self.bucket_name = bucket.name

                logging.info(f"Created new bucket '{bucket.name}' in {self}")

        super(GoogleCloudStorageDatalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(self, "cloud storage")

    def __str__(self):
        return f"{self.project_id} (Google Cloud Storage)"

    def list_objects(self, path):
        blobs = [blob.name.split("/")[-1] for blob in self.service.list_blobs(self.bucket_name, prefix=path)]
        return list(filter(None, blobs))

    def create_folder(self, path, folder_name):
        full_path = f"{path}/{folder_name}/" if path else f"{folder_name}/"

        bucket = self.service.get_bucket(self.bucket_name)
        blob = bucket.blob(full_path)

        blob.upload_from_string("", content_type="application/x-www-form-urlencoded;charset=UTF-8")
        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        for blob in self.service.list_blobs(self.bucket_name, prefix=path):
            blob.delete()

        logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        bucket = self.service.get_bucket(self.bucket_name)
        blob = bucket.blob(f"{path}/{filename}")

        if filename.split(".")[-1] == "parquet":
            content_type = "application/octet-stream"
            blob.upload_from_file(io.BytesIO(content), content_type=content_type)
        else:
            content_type = "application/json"
            blob.upload_from_string(content, content_type=content_type)

        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

    def download_file(self, path, query="latest"):
        bucket = self.service.get_bucket(self.bucket_name)

        filename, timestamp = get_wanted_file(query, self.list_objects(path))

        blob = bucket.get_blob(f"{path}/{filename}")
        raw_data = io.BytesIO(blob.download_as_bytes())
        data = pd.read_parquet(raw_data) if filename.split(".")[-1] == "parquet" else json.loads(raw_data.getvalue())

        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
