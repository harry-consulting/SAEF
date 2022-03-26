import io
import json
import logging
import os
import shutil
from pathlib import Path

import pandas as pd
from django.db import models

from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class LocalDatalake(models.Model):
    root_path = models.CharField(max_length=500, default="", blank=True)

    def save(self, *args, **kwargs):
        # If the object is not yet created, create the root path folder structure.
        if not self.pk:
            if self.root_path:
                Path(self.abs_path).mkdir(parents=True, exist_ok=True)

        super(LocalDatalake, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        path = self.root_path if self.root_path else ""
        self.abs_path = os.path.abspath(path)

    def __str__(self):
        return f"Stored locally at {self.abs_path}"

    def list_objects(self, path):
        return os.listdir(f"{self.abs_path}/{path}")

    def create_folder(self, path, folder_name):
        full_path = f"{self.abs_path}/{path}/{folder_name}" if path else f"{self.abs_path}/{folder_name}"

        Path(full_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created folder '{folder_name}' in local datalake.")

    def delete_path(self, path):
        full_path = f"{self.abs_path}/{path}"

        os.remove(full_path) if os.path.isfile(full_path) else shutil.rmtree(full_path, ignore_errors=True)
        logger.info(f"Deleted path '{path}' in local datalake.")

    def upload_file(self, path, filename, content):
        mode = "wb" if filename.split(".")[-1] == "parquet" else "w"
        with open(f"{self.abs_path}/{path}/{filename}", mode) as file:
            file.write(content)

        logger.info(f"Uploaded '{filename}' to '{path}' in local datalake.")

    def download_file(self, path, query="latest"):
        filename, timestamp = get_wanted_file(query, self.list_objects(path))

        with open(f"{self.abs_path}/{path}/{filename}", "rb") as file:
            data = pd.read_parquet(io.BytesIO(file.read())) if filename.split(".")[-1] == "parquet" else json.load(file)

        logger.info(f"Read '{filename}' from local datalake.")

        return data, timestamp
