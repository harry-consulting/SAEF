import logging

from util.data_util import get_schema, get_data
from datasets.models import DatasetRun

logger = logging.getLogger(__name__)


def task_extract_metadata(**kwargs):
    """Extract current dataset metadata, including column count, row count and column names and types."""
    dataset_run = kwargs["dataset_run"]
    dataset = dataset_run.dataset

    try:
        data_df, timestamp = get_data(dataset, get_timestamp=True)
        column_types = get_schema(data_df)

        result = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"), "columns": column_types,
                  "column_count": len(list(data_df)), "row_count": len(data_df.index)}
        dataset_run.status = DatasetRun.Status.SUCCEEDED

        return result
    except Exception as e:
        logger.error(f"Error while extracting metadata from {dataset}: {e}")
        return {"error": type(e).__name__, "message": str(e)}
