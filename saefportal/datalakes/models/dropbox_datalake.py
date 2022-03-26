import io
import json
import logging

import pandas as pd
from django.db import models
from fernet_fields import EncryptedTextField

import util.dropbox_util as util
from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class DropboxDatalake(models.Model):
    username = models.CharField(max_length=100)
    root_path = models.CharField(max_length=500, default="", blank=True)
    token_cache = EncryptedTextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(json.loads(self.token_cache))
        self.path = f"/{self.root_path}/" if self.root_path else "/"

    def __str__(self):
        return f"{self.username} (Dropbox)"

    def list_objects(self, path):
        search_results = self.service.files_list_folder(f"{self.path}{path}")

        return [entry.name for entry in search_results.entries]

    def create_folder(self, path, folder_name):
        full_path = folder_name

        if path:
            full_path = f"{path}/{full_path}"

        self.service.files_create_folder_v2(f"{self.path}{full_path}")
        logger.info(f"Created folder '{folder_name}' in {self}.")

    def delete_path(self, path):
        self.service.files_delete_v2(f"{self.path}{path}".rstrip("/"))
        logger.info(f"Deleted path '{path}' in {self}.")

    def upload_file(self, path, filename, content):
        if isinstance(content, str):
            content = content.encode()

        self.service.files_upload(content, f"{self.path}{path}/{filename}", mute=True)
        logger.info(f"Uploaded '{filename}' to '{path}' in {self}.")

    def download_file(self, path, query="latest"):
        filename, timestamp = get_wanted_file(query, self.list_objects(path))
        _, resp = self.service.files_download(f"{self.path}{path}/{filename}")

        data = pd.read_parquet(io.BytesIO(resp.content)) if filename.split(".")[-1] == "parquet" else resp.json()
        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
