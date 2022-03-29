import logging

from analyzer.analyzers import AnalyzerActualDataset, AnalyzerExpectedDataset, AnalyzerComparisonDataset
from datasets.models import DatasetRun
from settings.models import Settings

logger = logging.getLogger(__name__)


def task_profile_dataset(**kwargs):
    """Analyze the current state of a dataset and compare it with the expected state."""
    dataset_run = kwargs["dataset_run"]

    try:
        analyzer_actual = AnalyzerActualDataset(dataset_run)
        actual_dataset_profile, actual_dataset_dict = analyzer_actual.execute()

        analyzer_expected = AnalyzerExpectedDataset(dataset_run, actual_dataset_profile)
        expected_dataset_profile = analyzer_expected.execute()

        analyzer_comparison = AnalyzerComparisonDataset(actual_dataset_profile, expected_dataset_profile)
        comparison_dataset_dict = analyzer_comparison.execute()

        dataset_run.status = get_run_status(dataset_run)

        # If it is the first profile, the degree of change is always 0.
        if len(dataset_run.dataset.get_profile_runs()) == 1:
            return {"degree_of_change": 0}
        else:
            return {"degree_of_change": comparison_dataset_dict["degree_of_change"]}
    except Exception as e:
        logger.error(f"Error while profiling {dataset_run.dataset}: {e}")
        return {"error": type(e).__name__, "message": str(e)}


def get_run_status(dataset_run):
    settings = Settings.objects.get()

    if run_failed(dataset_run, settings.profile_failed_threshold):
        return DatasetRun.Status.FAILED
    elif run_succeed_with_issue(dataset_run, settings.profile_expected_datasets_n, settings.profile_delta_deviation):
        return DatasetRun.Status.SUCCEEDED_ISSUE
    else:
        return DatasetRun.Status.SUCCEEDED


def run_failed(dataset_run, failed_threshold):
    return dataset_run.result["degree_of_change"] > failed_threshold


def run_succeed_with_issue(dataset_run, expected_datasets_n, profile_delta_deviation):
    dataset_runs = dataset_run.dataset.get_profile_runs()[:expected_datasets_n]

    dataset_runs = filter(lambda x: x.result is not None and x.result["degree_of_change"] is not None, dataset_runs)
    list_of_degree_of_change = [*map(lambda x: x.result["degree_of_change"], dataset_runs)]
    historical_average_of_degree_of_change = sum(list_of_degree_of_change) / len(list_of_degree_of_change)

    difference = historical_average_of_degree_of_change * profile_delta_deviation
    upper_bound = historical_average_of_degree_of_change + difference

    return upper_bound < dataset_run.result["degree_of_change"]
