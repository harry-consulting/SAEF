import io
import json
import os
from collections import defaultdict

import requests
from django.db import models
from fernet_fields import EncryptedTextField

import util.one_drive_util as util
from datastores.models.file_datastore import FileDatastore
from datastores.util import get_supported_file_types


class OneDriveDatastore(FileDatastore):
    username = models.CharField(max_length=100)
    root_path = models.CharField(max_length=500, default="", blank=True)
    token_cache = EncryptedTextField()

    def __init__(self, *args, **kwargs):
        super(OneDriveDatastore, self).__init__(*args, **kwargs)
        self.base_endpoint = "https://graph.microsoft.com/v1.0/me/drive/root"

        if self.root_path:
            self.base_endpoint += f":/{self.root_path}:"

        self.token = util.get_token_from_cache(self)

    def __str__(self):
        return f"{self.username} (OneDrive)"

    def get_connection_details(self):
        return f"Username: {self.username}, Root path: {self.root_path}"

    def is_connection_valid(self):
        endpoint = f"{self.base_endpoint}/children"

        # Retrieve all files (with download urls) from the given folder path.
        r = requests.get(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})

        return True if r.status_code == 200 else False

    def get_viable_datasets(self):
        files = []
        file_type_groups = get_supported_file_types()

        # Note that it is only possible to search for two terms at a time so we chunk the file types in groups of two.
        chunked_file_type_groups = [file_type_groups[x:x + 2] for x in range(0, len(file_type_groups), 2)]

        for file_types in chunked_file_type_groups:
            endpoint = f"{self.base_endpoint}/search(q='{' '.join(file_types)}')"

            # Collecting viable datasets from the potentially paged search results.
            while endpoint:
                r = requests.get(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]})
                files.extend([item for item in r.json()["value"]
                              if "file" in item and item["name"].split(".")[-1] in file_types])

                endpoint = r.json()["@odata.nextLink"] if "@odata.nextLink" in r.json() else None

        viable_datasets = defaultdict(list)
        for file in files:
            parent_folder = file["parentReference"]["name"] if "name" in file["parentReference"] else "root"

            value = json.dumps({"id": file["id"], "name": os.path.splitext(file["name"])[0]})
            viable_datasets[parent_folder].append({"value": value, "display": file["name"]})

        return {"Files": dict(viable_datasets)}

    def _download_data(self, file_id):
        endpoint = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"

        item = requests.get(endpoint, headers={"Authorization": "Bearer " + self.token["access_token"]}).json()
        data = io.BytesIO(requests.get(item["@microsoft.graph.downloadUrl"]).content)
        file_type = item["name"].split(".")[-1]

        return data, file_type
