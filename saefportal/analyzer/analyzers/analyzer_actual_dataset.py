from analyzer.models import ActualDatasetProfile
from util.data_util import get_schema, get_data
from .analyzer import Analyzer
from .analyzer_actual_column import AnalyzerActualColumn
from .util import calculate_hash_sum


class AnalyzerActualDataset(Analyzer):
    def __init__(self, dataset_run):
        super().__init__()
        self.dataset_run = dataset_run

    def _execute_session(self):
        dataset = self.dataset_run.dataset
        data_df = get_data(dataset)
        column_types = get_schema(data_df)

        profile = {
            "column": {},
            "row_count": len(data_df.index),
            "column_count": len(list(data_df))
        }

        dataset_profile = ActualDatasetProfile.objects.create(dataset_run=self.dataset_run,
                                                              row_count=profile["row_count"],
                                                              column_count=profile["column_count"])

        columns = list(data_df)
        for index, column in enumerate(columns):
            analyzer = AnalyzerActualColumn(data_df, column_types, dataset_profile, column, profile["row_count"], index)
            profile["column"][column] = analyzer.execute()

        profile["hash_sum"] = calculate_hash_sum(profile)

        dataset_profile.hash_sum = profile["hash_sum"]
        dataset_profile.save()

        return dataset_profile, profile
