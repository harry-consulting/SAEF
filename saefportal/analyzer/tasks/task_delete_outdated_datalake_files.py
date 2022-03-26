from datetime import datetime

from datasets.models import Dataset
from settings.models import Settings


def task_delete_outdated_datalake_files(threshold_minutes):
    """Go through each dataset and delete outdated versions of the dataset in the datalake, if necessary."""
    datalake = Settings.objects.get().datalake
    now = datetime.now()

    for dataset in Dataset.objects.all():
        data_files = datalake.list_objects(f"{dataset.get_datalake_path()}/data")

        # If there is more than one file, delete duplicate snapshots if they are older than the given threshold.
        if len(data_files) > 1:
            for file in sorted(data_files)[:-1]:
                format = "%Y_%m_%d__%H_%M_%S"
                file_time = datetime.strptime(file.split(".")[0], format)

                if (now - file_time).total_seconds() / 60.0 > threshold_minutes:
                    datalake.delete_path(f"{dataset.get_datalake_path()}/data/{file}")
                    datalake.delete_path(f"{dataset.get_datalake_path()}/meta/preview_{file}")
                    datalake.delete_path(f"{dataset.get_datalake_path()}/meta/schema_{file.split('.')[0]}.json")
