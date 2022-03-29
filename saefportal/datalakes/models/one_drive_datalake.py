import logging

import pandas as pd
import requests
from django.db import models
from fernet_fields import EncryptedTextField

from util.one_drive_util import get_token_from_cache
from datalakes.util import get_wanted_file

logger = logging.getLogger(__name__)


class OneDriveDatalake(models.Model):
    username = models.CharField(max_length=100)
    root_path = models.CharField(max_length=500, default="", blank=True)
    token_cache = EncryptedTextField()

    def __init__(self, *args, **kwargs):
        super(OneDriveDatalake, self).__init__(*args, **kwargs)
        self.base_endpoint = "https://graph.microsoft.com/v1.0/me/drive/root:"

        if self.root_path:
            self.base_endpoint += f"/{self.root_path}"

        self.token = get_token_from_cache(self)

    def __str__(self):
        return f"{self.username} (OneDrive)"

    def list_objects(self, path):
        endpoint = f"{self.base_endpoint}/{path}:/children"
        r = requests.get(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})

        return [path_object["name"] for path_object in r.json().get("value", [])]

    def create_folder(self, path, folder_name):
        endpoint = f"{self.base_endpoint}/{path}:/children/"
        drive_item = {"name": folder_name, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}

        r = requests.post(endpoint, json=drive_item, headers={"Authorization": "Bearer " + self.token["access_token"]})
        logger.info(f"Created folder '{folder_name}' in {self}: {r.json()}")

    def delete_path(self, path):
        endpoint = f"{self.base_endpoint}/{path}"

        r = requests.delete(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})
        logger.info(f"Deleted path '{path}' in {self}: {r.status_code}")

    def upload_file(self, path, filename, content):
        # If the size of the content is smaller than 4MB upload the file in one step.
        if len(content) < 4000000:
            endpoint = f"{self.base_endpoint}/{path}/{filename}:/content"

            r = requests.put(endpoint, data=content, headers={"Authorization": "Bearer " + self.token["access_token"]})
            logger.info(f"Uploaded '{filename}' to '{path}' in {self}: {r.json()}")
        # If not, use an upload session to upload the file in sequential API requests.
        else:
            content_length = len(content)

            endpoint = f"{self.base_endpoint}/{path}/{filename}:/createUploadSession"
            r = requests.post(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})
            logger.info(f"Started upload session for uploading '{filename}' to '{path}' in {self}.")

            status = 202
            next_expected_ranges = ["0-"]
            upload_url = r.json()["uploadUrl"]

            # Keep going until the status code is HTTP 201 CREATED or HTTP 200 OK.
            while status == 202:
                # Handling potentially multiple expected ranges since data might be missing in the middle of the file.
                for next_range in next_expected_ranges:
                    next_start = int(next_range.split("-")[0])

                    # Using 3932160 as the range size since it is the largest multiple of 320 KiB smaller than 4 MB.
                    # Using byte range sizes that are not multiples of 320 KiB can cause errors with large files.
                    next_content = content[next_start:next_start + 3932160]
                    content_range = f"bytes {next_start}-{next_start + len(next_content) - 1}/{content_length}"

                    logger.info(f"Uploading {content_range}")

                    r = requests.put(upload_url, data=next_content,
                                     headers={"Content-Length": str(len(next_content)),
                                              "Content-Range": content_range})

                    if "nextExpectedRanges" in r.json():
                        next_expected_ranges = r.json()["nextExpectedRanges"]

                    status = r.status_code
            else:
                logger.info(f"Finished upload session: {r.json()}")

    def download_file(self, path, query="latest"):
        endpoint = f"{self.base_endpoint}/{path}:/children"

        # Retrieve all files (with download urls) from the given folder path.
        r = requests.get(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})

        # Map file names to download URLs.
        file_download_urls = {file["name"]: file["@microsoft.graph.downloadUrl"] for file in r.json().get("value", [])}

        # Find the wanted file and download the contents of the file to a dataframe.
        filename, timestamp = get_wanted_file(query, list(file_download_urls))

        if filename.split(".")[-1] == "parquet":
            data = pd.read_parquet(file_download_urls[filename])
        else:
            data = requests.get(file_download_urls[filename]).json()

        logger.info(f"Downloaded '{filename}' from {self}.")

        return data, timestamp
