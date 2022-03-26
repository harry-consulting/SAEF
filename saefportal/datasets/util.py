import json

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from util.dropbox_util import start_dropbox_authentication
from util.google_util import start_google_authentication
from util.one_drive_util import start_one_drive_authentication
from util.data_util import get_schema, get_data
from datasets import models
from datasets.models import Dataset, Connection
from datastores.models import (PostgresDatastore, AzureDatastore, AzureBlobStorageDatastore, AzureDataLakeDatastore,
                               AmazonS3Datastore)
from datastores.util import initialize_connection


def data_overview(dataset):
    """
    Return information used to get an overview of the datasets data (column types and data preview). Also return the
    timestamp of when this information is from.
    """

    try:
        data_preview, timestamp = get_data(dataset, preview=True, get_timestamp=True)
        column_types = get_schema(data_preview)

        # Handle null values and convert the dataframe into a list of tuples.
        data_preview.fillna("[null]", inplace=True)
        data_preview = list(data_preview.itertuples(index=False, name=None))

        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # If the data overview cannot be retrieved from either the datalake or datastore, set to None to alert the user.
        data_preview, column_types, timestamp = [], None, None

    return timestamp, column_types, data_preview


def remove_non_datastore_keys(form_data):
    """Remove keys not relevant to creating a datastore object."""
    form_dict = {k: v[0] for k, v in form_data.items()}

    for key in ["csrfmiddlewaretoken", "name", "type", "owner"]:
        form_dict.pop(key, None)

    return form_dict


def create_database_datastore(form_data):
    """Create a Postgres or Azure object based on the given connection and form data."""
    datastore_type = form_data.get("type", None)
    form_dict = remove_non_datastore_keys(dict(form_data))

    # Create the datastore object with the remaining data.
    if datastore_type == models.Connection.Type.POSTGRES:
        datastore_object = PostgresDatastore(**form_dict)
    else:
        datastore_object = AzureDatastore(**form_dict)

    return datastore_object


def remove_existing_datasets(viable_datasets, connection):
    """Remove the viable datasets that are already existing datasets."""
    for dataset_type in viable_datasets:
        for container, datasets in viable_datasets[dataset_type].items():
            actually_viable_datasets = []

            for viable_dataset in datasets:
                # For file datastores, check that the ID in the value is not already a dataset file ID.
                if dataset_type == "Files":
                    file_id = json.loads(viable_dataset["value"])["id"]
                    if not Dataset.objects.filter(file_id=file_id, connection=connection).exists():
                        actually_viable_datasets.append(viable_dataset)

                # For relational datastores, check that the value is not already a dataset name.
                elif not Dataset.objects.filter(name=viable_dataset["value"], connection=connection).exists():
                    actually_viable_datasets.append(viable_dataset)

            viable_datasets[dataset_type][container] = actually_viable_datasets

        # Remove potentially empty folders.
        viable_datasets[dataset_type] = {k: v for k, v in viable_datasets[dataset_type].items() if v}

    return viable_datasets


def import_datasets(datasets, form):
    """
    "Import" the given datasets by creating dataset objects using the given form values. The data from each dataset is
    uploaded to the datalake automatically using a signal.
    """
    for dataset in datasets:
        dataset_type, dataset_id = dataset.split(".", 1)
        dataset_type = dataset_type[:-1].upper()

        # Fields shared between both database datasets and file datasets.
        common = {"owner": form.cleaned_data["owner"], "tags": form.cleaned_data["tags"],
                  "connection": form.cleaned_data["connection"]}

        if dataset_type in ["TABLE", "VIEW"]:
            dataset = models.Dataset.objects.create(name=dataset_id, type=dataset_type, table=dataset_id, **common)
        else:
            value = json.loads(dataset_id)
            dataset = models.Dataset.objects.create(name=value["name"], type="TABLE", file_id=value["id"], **common)

        dataset.contacts.add(*form.cleaned_data["contacts"])


def get_uploaded_datasets():
    """Return a dict with uploaded datasets under the category "TABLE"."""
    related_datasets = Dataset.objects.filter(connection=None).order_by("name")

    return {"TABLE": list(related_datasets)}


def group_connection_types():
    """Return the possible connection types, grouped into the categories "Relational", "File-based" and "BLOB-based"."""
    return {"Relational": [Connection.Type.AZURE, Connection.Type.POSTGRES],
            "File-based": [Connection.Type.DROPBOX, Connection.Type.GOOGLE_DRIVE, Connection.Type.ONEDRIVE],
            "BLOB-based": [Connection.Type.AZURE_BLOB_STORAGE, Connection.Type.AZURE_DATA_LAKE,
                           Connection.Type.AMAZON_S3, Connection.Type.GOOGLE_CLOUD_STORAGE]}


def connect_to_datastore(request, form):
    connection_type = form.data["type"]

    if connection_type == "ONEDRIVE":
        return start_one_drive_authentication(request, form, "datastore")
    elif connection_type == "GOOGLE_DRIVE":
        return start_google_authentication(request, form, "datastore")
    elif connection_type == "GOOGLE_CLOUD_STORAGE":
        return start_google_authentication(request, form, "datastore")
    elif connection_type == "DROPBOX":
        return start_dropbox_authentication(request, form, "datastore")
    else:
        if connection_type in ["POSTGRES", "AZURE"]:
            ds = create_database_datastore(form.data)
            ds.save()
        elif connection_type == "AZURE_BLOB_STORAGE":
            ds = AzureBlobStorageDatastore.objects.create(connection_string=form.data["connection_string"],
                                                          container_name=form.data["blob_container"])
        elif connection_type == "AZURE_DATA_LAKE":
            ds = AzureDataLakeDatastore.objects.create(connection_string=form.data["connection_string"],
                                                       container_name=form.data["blob_container"])
        else:
            ds = AmazonS3Datastore.objects.create(access_key_id=form.data["access_key_id"],
                                                  secret_access_key=form.data["secret_access_key"],
                                                  bucket_name=form.data["bucket_name"])

        initialize_connection(ds, form.data["name"], form.data["owner"], connection_type, request)

    return HttpResponseRedirect(reverse_lazy("datasets:index"))
