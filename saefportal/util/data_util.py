import logging
from datetime import datetime

from settings.models import Settings

logger = logging.getLogger(__name__)


def get_data(dataset, preview=False, get_timestamp=False):
    """
    Based on the settings and current accessibility of the data, get the data from either the datastore or datalake.
    The latest data is always returned. If "preview" is True, only return the first 50 rows of the data.
    """
    settings = Settings.objects.get()
    connection = dataset.connection

    datalake = settings.datalake
    dataset_datalake_path = dataset.get_datalake_path()

    path = f"{dataset_datalake_path}/meta" if preview else f"{dataset_datalake_path}/data"
    latest = "latest preview" if preview else "latest"

    # Use the datastore or the datalake based on the settings. If one method fails, fall back to the other.
    if settings.try_live_connection and connection and connection.datastore.is_connection_valid():
        try:
            data_df = connection.datastore.retrieve_data(dataset, limit=50 if preview else None)
            timestamp = datetime.now()
        except Exception:
            logger.error(f"Not able to retrieve data from datastore {connection.datastore}. Using datalake {datalake}.")
            data_df, timestamp = datalake.download_file(path, latest)
    else:
        try:
            data_df, timestamp = datalake.download_file(path, latest)
        except Exception:
            logger.error(f"Not able to retrieve data from datalake {datalake}. Using datastore {connection.datastore}.")
            data_df = connection.datastore.retrieve_data(dataset, limit=50 if preview else None)
            timestamp = datetime.now()

    if get_timestamp:
        return data_df, timestamp
    else:
        return data_df


def get_schema(data_df):
    """Return dict from column names to the corresponding column type."""
    return {col_name: str(data_df[col_name].dtype) for col_name in list(data_df)}
