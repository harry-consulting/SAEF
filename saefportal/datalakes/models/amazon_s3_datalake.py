import json
import logging
import uuid
from io import BytesIO

import boto3
import pandas as pd
from django.db import models
from fernet_fields import EncryptedCharField

from util.amazon_s3_util import get_aws_account_username
from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class AmazonS3Datalake(models.Model):
    username = models.CharField(max_length=100)
    bucket_name = models.CharField(max_length=200)
    access_key_id = EncryptedCharField(max_length=128)
    secret_access_key = EncryptedCharField(max_length=128)

    def save(self, *args, **kwargs):
        # If the object is not yet created, set the aws username and, if necessary, create a bucket.
        if not self.pk:
            self.username = get_aws_account_username(self.access_key_id, self.secret_access_key)

            if self.bucket_name not in [bucket.name for bucket in self.s3.buckets.all()]:
                new_bucket_name = self.bucket_name if self.bucket_name else f"saef-{uuid.uuid4()}"
                self.s3.create_bucket(Bucket=new_bucket_name)
                self.bucket_name = new_bucket_name

                logging.info(f"Created new bucket '{new_bucket_name}' in {self}.")

        super(AmazonS3Datalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.s3 = boto3.resource("s3", aws_access_key_id=self.access_key_id,
                                 aws_secret_access_key=self.secret_access_key)

    def __str__(self):
        return f"{self.username} (Amazon S3)"

    def list_objects(self, path):
        bucket = self.s3.Bucket(self.bucket_name)

        objects = [bucket_object.key.split("/")[-1] for bucket_object in bucket.objects.filter(Prefix=path)]
        return list(filter(None, objects))

    def create_folder(self, path, folder_name):
        bucket = self.s3.Bucket(self.bucket_name)
        full_path = f"{path}/{folder_name}/" if path else f"{folder_name}/"

        bucket.put_object(Key=full_path)
        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        bucket = self.s3.Bucket(self.bucket_name)

        bucket.objects.filter(Prefix=path).delete()
        logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        bucket = self.s3.Bucket(self.bucket_name)
        obj = bucket.Object(f"{path}/{filename}")

        data = BytesIO(content) if filename.split(".")[-1] == "parquet" else BytesIO(bytes(content, encoding="utf-8"))
        obj.upload_fileobj(data)
        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

    def download_file(self, path, query="latest"):
        bucket = self.s3.Bucket(self.bucket_name)

        filename, timestamp = get_wanted_file(query, self.list_objects(path))

        raw_data = BytesIO()
        bucket.download_fileobj(f"{path}/{filename}", raw_data)
        data = pd.read_parquet(raw_data) if filename.split(".")[-1] == "parquet" else json.loads(raw_data.getvalue())

        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
