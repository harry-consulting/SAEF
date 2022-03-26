import json
import logging
from io import BytesIO

import pandas as pd
from django.db import models
from fernet_fields import EncryptedTextField
from googleapiclient.http import MediaIoBaseUpload

import util.google_util as util
from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class GoogleDriveDatalake(models.Model):
    username = models.CharField(max_length=100)
    root_path = models.CharField(max_length=500, default="", blank=True)
    token_cache = EncryptedTextField()
    # Since both folders and files are accessed through their IDs and not a path, we save the IDs for easier access.
    object_ids = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        # If the object is not yet created, get the username from the API.
        if not self.pk:
            self.username = self.service.about().get(fields="user").execute()["user"]["emailAddress"]

        super(GoogleDriveDatalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(self, "drive")

    def __str__(self):
        return f"{self.username} (Google Drive)"

    def list_objects(self, path):
        parent_folder = self.object_ids[path]

        response = self.service.files().list(q=f"'{parent_folder}' in parents", spaces="drive").execute()

        return [file["name"] for file in response.get("files", [])]

    def create_folder(self, path, folder_name):
        if path:
            parent_folder = [self.object_ids[path]]
        else:
            parent_folder = [util.get_root_folder_id(self.service, self.root_path)] if self.root_path else []

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": parent_folder,
        }
        file = self.service.files().create(body=folder_metadata, fields="id").execute()

        # Save the folder id to make it possible to use it as a parent folder later.
        full_path = f"{path}/{folder_name}" if path else folder_name
        self.object_ids[full_path] = file.get("id")
        self.save()

        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        object_id = self.object_ids.pop(path.rstrip("/"), None)
        self.save()

        if object_id:
            self.service.files().delete(fileId=object_id).execute()
            logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        file_metadata = {
            "name": filename,
            "parents": [self.object_ids[path]]
        }

        mime_type = "application/octet-stream" if filename.split(".")[-1] == "parquet" else "application/json"
        data = BytesIO(content) if filename.split(".")[-1] == "parquet" else BytesIO(bytearray(content, "utf-16"))
        media = MediaIoBaseUpload(data, mimetype=mime_type)

        response = self.service.files().create(body=file_metadata, media_body=media).execute()
        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

        # Save the file id to make it easier to access later.
        self.object_ids[f"{path}/{filename}"] = response["id"]
        self.save()

    def download_file(self, path, query="latest"):
        parent_folder = self.object_ids[path]

        # Find all files in the given path.
        response = self.service.files().list(q=f"'{parent_folder}' in parents", spaces="drive").execute()

        # Map file names to ids.
        file_ids = {file["name"]: file["id"] for file in response.get("files", [])}

        # Find the wanted file and download the contents of the file.
        filename, timestamp = get_wanted_file(query, list(file_ids))
        raw_data = util.download_data(self.service, file_ids[filename])

        data = pd.read_parquet(raw_data) if filename.split(".")[-1] == "parquet" else json.loads(raw_data.getvalue())
        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
