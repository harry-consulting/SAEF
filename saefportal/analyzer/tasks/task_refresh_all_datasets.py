from analyzer.tasks.task_refresh_data import task_refresh_data
from datasets.models import Dataset, DatasetRun


def task_refresh_all_datasets():
    """Go through all current datasets and refresh the locally stored version of the dataset."""
    for dataset in Dataset.objects.all():
        temp_dataset_run = DatasetRun.objects.create(dataset=dataset, task_name="Refresh data")

        task_refresh_data(dataset_run=temp_dataset_run, task_parameters={})
        temp_dataset_run.delete()
