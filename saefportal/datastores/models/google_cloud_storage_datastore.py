import io

from django.db import models
from fernet_fields import EncryptedTextField

import util.google_util as util
from datastores.models.file_datastore import FileDatastore
from datastores.util import get_viable_blob_datasets


class GoogleCloudStorageDatastore(FileDatastore):
    username = models.CharField(max_length=100)
    project_id = models.CharField(max_length=500)
    token_cache = EncryptedTextField()
    bucket_name = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        # If the object is not yet created, get the username from the API.
        if not self.pk:
            self.username = self.service.get_service_account_email()

        super(GoogleCloudStorageDatastore, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(self, "cloud storage")
        self.bucket = self.service.get_bucket(self.bucket_name)

    def __str__(self):
        return f"{self.project_id} (Google Cloud Storage)"

    def get_connection_details(self):
        return f"Username: {self.username}, Project ID: {self.project_id}, Bucket name: {self.bucket_name}"

    def is_connection_valid(self):
        # Since refresh tokens no not expire we assume that the connection is always valid.
        return True

    def get_viable_datasets(self):
        return get_viable_blob_datasets(self.service.list_blobs(bucket_or_name=self.bucket), "name")

    def _download_data(self, file_id):
        data = io.BytesIO(self.bucket.blob(file_id).download_as_bytes())
        file_type = file_id.split(".")[-1]

        return data, file_type
