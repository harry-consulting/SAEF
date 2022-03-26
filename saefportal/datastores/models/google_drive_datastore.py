import io
import json
import os.path
from collections import defaultdict

from django.db import models
from fernet_fields import EncryptedTextField

import util.google_util as util
from datastores.models.file_datastore import FileDatastore
from datastores.util import get_supported_file_types


class GoogleDriveDatastore(FileDatastore):
    username = models.CharField(max_length=100)
    token_cache = EncryptedTextField()
    root_path = models.CharField(max_length=500, default="", blank=True)
    root_folder_id = models.CharField(max_length=100, blank=True, null=True)

    # Cache used for storing folder names to avoid repeatedly finding names from ids when getting viable datasets.
    folder_names = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        # If the object is not yet created, get the username and root folder id from the API.
        if not self.pk:
            self.username = self.service.about().get(fields="user").execute()["user"]["emailAddress"]

            if self.root_path:
                self.root_folder_id = util.get_root_folder_id(self.service, self.root_path)

        super(GoogleDriveDatastore, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(self, "drive")

    def __str__(self):
        return f"{self.username} (Google Drive)"

    def get_connection_details(self):
        return f"Username: {self.username}, Root path: {self.root_path}"

    def is_connection_valid(self):
        # Since refresh tokens no not expire we assume that the connection is always valid.
        return True

    def _get_root_folder_files(self, service):
        page_token = None
        items = []

        # Using a page token to get all files since there are potentially more than 100 files.
        while True:
            response = service.files().list(q="", spaces="drive", fields="files(id, name, mimeType, parents)",
                                            pageToken=page_token).execute()
            items.extend([file for file in response.get("files", [])])

            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        folders, files = [], []
        for item in items:
            folders.append(item) if item["mimeType"] == "application/vnd.google-apps.folder" else files.append(item)

        # If there is a user defined root folder then limit the files to be within that folder.
        if self.root_path:
            viable_parents = [self.root_folder_id]
            current_parents = [self.root_folder_id]

            # Iteratively walk down the folders from the user defined root folder until we reach the bottom.
            while current_parents:
                current_parents = [folder["id"] for folder in folders if folder["parents"][0] in current_parents]
                viable_parents.extend(current_parents)

            # Only allow files that have a parent in the viable parents list.
            files = [file for file in files if file["parents"][0] in viable_parents]

        return files

    def _get_parent_folder_names(self, service, files):
        """Return a dict from the given files' parent folder ids to their corresponding names."""
        parents = {}
        parent_ids = list(set([file["parents"][0] for file in files]))

        for parent_id in parent_ids:
            # Check if the parent folder id has been seen before. If not, make a request to get the name.
            if parent_id in self.folder_names:
                parents[parent_id] = self.folder_names[parent_id]
            else:
                response = service.files().get(fileId=parent_id, fields="name").execute()
                parents[parent_id] = response.get("name")

                self.folder_names[parent_id] = response.get("name")

        self.save()

        return parents

    def get_viable_datasets(self):
        root_files = self._get_root_folder_files(self.service)

        # Filter away files that are not csv, parquet, avro or xlsx.
        files = [file for file in root_files if file["name"].split(".")[-1] in get_supported_file_types()]

        # Convert the parent ids to names that can be used to group the files in the UI.
        parents = self._get_parent_folder_names(self.service, files)

        viable_datasets = defaultdict(list)

        for file in files:
            parent_folder = parents[file["parents"][0]]

            value = json.dumps({"id": file["id"], "name": os.path.splitext(file["name"])[0]})
            viable_datasets[parent_folder].append({"value": value, "display": file["name"]})

        return {"Files": dict(viable_datasets)}

    def _download_data(self, file_id):
        data = io.BytesIO(util.download_data(self.service, file_id).getvalue())

        # Get the name to find the file type.
        response = self.service.files().get(fileId=file_id, fields="name").execute()
        file_type = response.get("name").split(".")[-1]

        return data, file_type
