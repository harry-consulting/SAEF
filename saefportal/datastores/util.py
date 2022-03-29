import json
from collections import defaultdict

import fastavro
import pandas as pd
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from datasets.models import Connection
from users.models import User


def get_supported_file_types():
    """Return a list of the viable file type extensions."""
    return ["csv", "avro", "parquet", "xlsx", "xls", "xlsm", "xlsb"]


def initialize_connection(datastore, connection_name, connection_owner_id, connection_type, request):
    """Create a connection and save the datastore on the connection object for later use."""
    owner = User.objects.get(id=connection_owner_id)
    connection = Connection.objects.create(name=connection_name, owner=owner, type=connection_type)

    connection.datastore = datastore
    connection.save()

    messages.success(request, "Connection was created.")
    return HttpResponseRedirect(reverse("datasets:index"))


def get_query(dataset, query):
    """Go through the potentially None valued given dataset and query and extract the query."""
    if query:
        return query
    elif dataset.query:
        return dataset.query
    else:
        return f"SELECT * FROM {dataset.table}"


def structure_tables_views(table, views):
    """Return a structured dictionary containing the given tables and views."""
    table_dict = defaultdict(list)
    [table_dict[schema].append({"value": f"{schema}.{table}", "display": table}) for (schema, table) in table]

    view_dict = defaultdict(list)
    [view_dict[schema].append({"value": f"{schema}.{view}", "display": view}) for (schema, view) in views]

    return {"Tables": dict(table_dict), "Views": dict(view_dict)}


def convert_to_dataframe(file_type, data):
    """Convert the given bytes data into a dataframe based on the given file type."""
    if file_type == "csv":
        df = pd.read_csv(data, sep=None)
    elif file_type == "avro":
        df = pd.DataFrame.from_records(fastavro.reader(data))
    elif file_type == "parquet":
        df = pd.read_parquet(data)
    else:
        df = pd.read_excel(data)

    return df


def get_viable_blob_datasets(blobs, name_attr):
    """
    Used to get the viable datasets for blob datastores. Used for Google Cloud Storage, Azure Blob Storage,
    Azure Data Lake and Amazon S3 datastores.
    """
    viable_blobs = []
    for blob in blobs:
        if getattr(blob, name_attr).split(".")[-1].lower() in get_supported_file_types():
            viable_blobs.append(blob)

    viable_datasets = defaultdict(list)
    for blob in viable_blobs:
        split_path = getattr(blob, name_attr).split("/")
        parent_folder = split_path[-2] if len(split_path) >= 2 else "root"

        value = json.dumps({"id": getattr(blob, name_attr), "name": split_path[-1].split(".")[0]})
        viable_datasets[parent_folder].append({"value": value, "display": split_path[-1]})

    return {"Files": dict(viable_datasets)}
