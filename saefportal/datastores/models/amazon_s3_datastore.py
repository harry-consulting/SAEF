import io

import boto3
from django.db import models
from fernet_fields import EncryptedCharField

from util.amazon_s3_util import get_aws_account_username
from datastores.models.file_datastore import FileDatastore
from datastores.util import get_viable_blob_datasets


class AmazonS3Datastore(FileDatastore):
    username = models.CharField(max_length=100)
    bucket_name = models.CharField(max_length=200)
    access_key_id = EncryptedCharField(max_length=128)
    secret_access_key = EncryptedCharField(max_length=128)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the aws username.
        if not self.pk:
            self.username = get_aws_account_username(self.access_key_id, self.secret_access_key)

        super(AmazonS3Datastore, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.s3 = boto3.resource("s3", aws_access_key_id=self.access_key_id,
                                 aws_secret_access_key=self.secret_access_key)
        self.bucket = self.s3.Bucket(self.bucket_name)

    def __str__(self):
        return f"{self.username} (Amazon S3)"

    def get_connection_details(self):
        return f"Access key ID: {self.access_key_id}, Secret access key: {self.secret_access_key}, " \
               f"Bucket name: {self.bucket_name}"

    def is_connection_valid(self):
        # If the key id and key are valid (needed to initialize the object), we assume the connection is valid.
        return True

    def get_viable_datasets(self):
        return get_viable_blob_datasets(self.bucket.objects.all(), "key")

    def _download_data(self, file_id):
        data = io.BytesIO()
        self.bucket.download_fileobj(file_id, data)
        file_type = file_id.split(".")[-1]

        return io.BytesIO(data.getvalue()), file_type
