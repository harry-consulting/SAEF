import io
import json
import uuid
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from util.data_util import get_schema
from datasets.models import Connection, Dataset
from datastores.util import convert_to_dataframe
from settings.models import Settings


def create_initial_datalake_folder_structure(datalake):
    datalake.create_folder("", "saef")
    datalake.create_folder("saef", "work")
    datalake.create_folder("saef", "gold")
    datalake.create_folder("saef", "landing")
    datalake.create_folder("saef/landing", "uploads")


def initialize_datalake(datalake, request, migrate=False):
    """
    Create the initial folder structure and save the datalake in the settings for later use. If migrate is True, migrate
    the data from the previous datalake to the new datalake.
    """
    settings = Settings.objects.get()
    old_datalake = settings.datalake
    settings.datalake = datalake
    settings.save()

    create_initial_datalake_folder_structure(datalake)

    if migrate:
        migrate_data(old_datalake, datalake)
    elif old_datalake:
        old_datalake.delete()

    messages.success(request, "Migrated data to new datalake." if migrate else "Connection to datalake established.")
    return HttpResponseRedirect(reverse("settings:settings", args=(1,)))


def migrate_data(old_datalake, new_datalake):
    """Move the latest data from the given old datalake to the given new datalake."""
    # Create the connection folder structure used in the old datalake, in the new datalake.
    for connection in Connection.objects.all():
        new_datalake.create_folder("saef/landing", connection.name)

    for dataset in Dataset.objects.all():
        # Create the dataset folder structure used in the old datalake, in the new datalake.
        datalake_path = dataset.get_datalake_path()
        [path, folder_name] = datalake_path.rsplit('/', 1)

        new_datalake.create_folder(path, folder_name)
        new_datalake.create_folder(datalake_path, "data")
        new_datalake.create_folder(datalake_path, "meta")

        # Download the latest data from the old datalake and upload it to the new.
        latest_data, timestamp = old_datalake.download_file(f"{datalake_path}/data", "latest")
        latest_schema, _ = old_datalake.download_file(f"{datalake_path}/meta", "latest schema")

        save_data_to_datalake(latest_data, latest_schema, datalake_path, timestamp)

    old_datalake.delete()


def get_wanted_file(query, files):
    """
    The query can be either "latest", "latest preview", "latest schema" or a filename. Also returns the timestamp
    of the found file.
    """
    files = sorted(files)

    if query == "latest":
        file = files[-1]
    elif "latest" in query:
        search_term = query.split()[1]
        file = [x for x in files if search_term in x][-1]
    else:
        file = next((x for x in files if x == query), None)

    format = "%Y_%m_%d__%H_%M_%S"
    timestamp = datetime.strptime(file.split(".")[0].replace("preview_", "").replace("schema_", ""), format)

    return file, timestamp


def convert_to_parquet(df, schema):
    """Return a buffer stream containing parquet data corresponding to the given dataframe."""
    df.columns = df.columns.astype(str)

    # Manually cast datatypes that are not supported by parquet, before converting.
    for column, column_type in schema.items():
        first_valid = df[column].first_valid_index()

        if first_valid is not None:
            # Convert UUID columns to string.
            if isinstance(df[column].iloc[first_valid], uuid.UUID):
                df[column] = df[column].astype(str)

    stream = io.BytesIO()
    df.to_parquet(stream, index=False, engine="pyarrow")

    return stream


def save_dataset_to_datalake(dataset):
    """Save a snapshot of the given dataset instance to the datalake. Saves the data, preview and schema."""
    datastore = dataset.connection.datastore
    data_df = datastore.retrieve_data(dataset)
    schema = get_schema(data_df)

    save_data_to_datalake(data_df, schema, dataset.get_datalake_path())


def save_upload_to_datalake(file):
    """Save data uploaded from the users local environment to the datalake. Saves the data, preview and schema."""
    [file_name, file_type] = file.name.rsplit(".", 1)

    data_df = convert_to_dataframe(file_type, io.BytesIO(file.read()))
    schema = {col_name: str(data_df[col_name].dtype) for col_name in list(data_df)}

    save_data_to_datalake(data_df, schema, f"saef/landing/uploads/{file_name}")


def save_data_to_datalake(data_df, schema, dataset_path, time=None):
    """Save the given pandas dataframe and schema to the datalake."""
    if time is None:
        time = datetime.now()

    datalake = Settings.objects.get().datalake
    time_str = time.strftime("%Y_%m_%d__%H_%M_%S")
    preview_df = data_df.head(50)

    # Convert the data to parquet to save space in the datalake.
    data_stream = convert_to_parquet(data_df, schema)
    preview_stream = convert_to_parquet(preview_df, schema)

    # Upload the data, preview and schema to the folder structure in the datalake.
    datalake.upload_file(f"{dataset_path}/data", f"{time_str}.parquet", data_stream.getvalue())
    datalake.upload_file(f"{dataset_path}/meta", f"preview_{time_str}.parquet", preview_stream.getvalue())
    datalake.upload_file(f"{dataset_path}/meta", f"schema_{time_str}.json", json.dumps(schema, indent=4))
