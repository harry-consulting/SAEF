import io
import json
import os
from collections import defaultdict

from django.db import models
from fernet_fields import EncryptedTextField

import util.dropbox_util as util
from datastores.models.file_datastore import FileDatastore
from datastores.util import get_supported_file_types


class DropboxDatastore(FileDatastore):
    username = models.CharField(max_length=100)
    root_path = models.CharField(max_length=500, default="", blank=True)
    token_cache = EncryptedTextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = util.get_service_from_cache(json.loads(self.token_cache))
        self.path = f"/{self.root_path}/" if self.root_path else "/"

    def __str__(self):
        return f"{self.username} (Dropbox)"

    def get_connection_details(self):
        return f"Username: {self.username}, Root path: {self.root_path}"

    def is_connection_valid(self):
        # Since refresh tokens no not expire we assume that the connection is always valid.
        return True

    def get_viable_datasets(self):
        viable_datasets = defaultdict(list)

        search_results = self.service.files_list_folder("" if self.path == "/" else self.path, recursive=True)
        entries = search_results.entries

        # If the search results are paged, collect viable datasets from each page using the given cursor.
        while search_results.has_more:
            search_results = self.service.files_list_folder_continue(search_results.cursor)
            entries.extend(search_results.entries)

        for entry in entries:
            if entry.name.split(".")[-1].lower() in get_supported_file_types():
                parent_folder = entry.path_display.split("/")[-2]

                value = json.dumps({"id": entry.id, "name": os.path.splitext(entry.name)[0]})
                viable_datasets[parent_folder].append({"value": value, "display": entry.name})

        return {"Files": dict(viable_datasets)}

    def _download_data(self, file_id):
        file, response = self.service.files_download(file_id, rev=None)
        data = io.BytesIO(response.content)
        file_type = file.name.split(".")[-1]

        return data, file_type
