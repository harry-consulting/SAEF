import logging

from analyzer.tasks.task_profile_dataset import task_profile_dataset
from datalakes.util import save_dataset_to_datalake
from datasets.models import DatasetRun

logger = logging.getLogger(__name__)


def task_refresh_data(dataset_run, task_parameters):
    """Refresh the instance of the dataset saved in the datalake."""
    dataset = dataset_run.dataset

    # Check if the degree of change is above the given threshold before refreshing.
    if dataset.connection and degree_of_change_above_threshold(dataset_run, task_parameters):
        try:
            save_dataset_to_datalake(dataset)

            dataset_run.status = DatasetRun.Status.SUCCEEDED
            return {"refreshed": True}
        except Exception as e:
            logger.error(f"Error while refreshing {dataset} in datalake: {e}")
            return {"error": type(e).__name__, "message": str(e)}
    else:
        dataset_run.status = DatasetRun.Status.SUCCEEDED_ISSUE
        return {"refreshed": False}


def degree_of_change_above_threshold(dataset_run, task_parameters):
    """
    Return True if the actual degree of change is above the given threshold, False otherwise. If no threshold was given
    also return True.
    """
    if "degree_of_change_threshold" in task_parameters and task_parameters["degree_of_change_threshold"]:
        temp_dataset_run = DatasetRun.objects.create(dataset=dataset_run.dataset, task_name="Profile dataset")

        result = task_profile_dataset(dataset_run=temp_dataset_run)
        temp_dataset_run.delete()

        return ("degree_of_change" in result and
                result["degree_of_change"] > float(task_parameters["degree_of_change_threshold"]))
    else:
        return True
