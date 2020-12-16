""" define the top class for all analyzers  """
from __future__ import absolute_import, unicode_literals
from saefportal.settings import EXPECTED_DATASETS_N, EXPECTED_DATASET_COLUMN_DEFINITION_THRESHOLD
from saef.models import Dataset, DatasetSession
from .analyzer import Analyzer
from .utils import add_value, calculate_average
from .analyzer_expected_column import AnalyzerExpectedColumn

from analyzer.models import ActualColumnProfile, ActualDatasetProfile, ExpectedDatasetProfile


def initialize_profile():
    return {
        'row_count': [],
        'column_count': [],
        'column_definitions': [],
        'hash_sum': [],
        'column': {}
    }


def retrieve_most_common_column_definitions(column_definitions):
    column_definitions_dict = {}

    for column in column_definitions:
        for item in column:
            name = item[0]
            if name not in column_definitions_dict:
                column_definitions_dict[name] = []
            column_definitions_dict[name].append(item)

    common_columns = []
    for column in column_definitions_dict.values():
        if len(column) >= EXPECTED_DATASET_COLUMN_DEFINITION_THRESHOLD:
            common_columns.append(column[0])

    return common_columns


def initialize_column_profile(profile, name):
    if name not in profile['column']:
        profile['column'][name] = {}
        profile['column'][name]['min'] = []
        profile['column'][name]['max'] = []
        profile['column'][name]['uniqueness'] = []
        profile['column'][name]['hash_sum'] = []

    return profile['column'][name]


class AnalyzerExpectedDataset(Analyzer):
    def __init__(self, dataset_session_pk, actual_dataset):
        super().__init__()
        self.dataset_session_pk = dataset_session_pk
        self.actual_dataset = actual_dataset

    def _execute_session(self):
        dataset_session = DatasetSession.objects.get(pk=self.dataset_session_pk)
        datasets = ActualDatasetProfile.objects.filter(dataset_session__dataset=dataset_session.dataset).order_by('-pk')[:EXPECTED_DATASETS_N]

        datasets_count = len(datasets)
        if datasets_count == 0:
            return None

        profile = initialize_profile()

        profile['column_definitions'] = []

        # Addition of the retrieved datasets
        for ds in datasets:
            profile['row_count'] = add_value(profile['row_count'], ds.row_count)
            profile['column_count'] = add_value(profile['column_count'], ds.column_count)
            profile['hash_sum'] = add_value(profile['hash_sum'], ds.hash_sum)

            columns = ActualColumnProfile.objects.filter(dataset_profile=ds.id)

            column_definitions = []
            for col in columns:
                column = initialize_column_profile(profile, col.name)

                # Attributes used for average calculation
                column['min'] = add_value(column['min'], col.min)
                column['max'] = add_value(column['max'], col.max)
                column['uniqueness'] = add_value(column['uniqueness'], col.uniqueness)
                column['hash_sum'] = add_value(column['hash_sum'], col.hash_sum)

                # Attributes information
                column['datatype'] = col.datatype
                column['nullable'] = col.nullable
                column['order'] = col.order

                column_definitions.append((col.name, col.datatype, col.nullable, col.order))

            profile['column_definitions'].append(column_definitions)

        dataset_profile = ExpectedDatasetProfile.objects.create(actual_dataset_profile=self.actual_dataset,
                                                                row_count=calculate_average(profile['row_count']),
                                                                column_count=calculate_average(profile['column_count']),
                                                                hash_sum=calculate_average(profile['hash_sum']))

        common_column_definitions = retrieve_most_common_column_definitions(profile['column_definitions'])

        for col in common_column_definitions:
            column = profile['column'][col[0]]
            analyzer = AnalyzerExpectedColumn(dataset_profile, col[0], column)
            analyzer.execute()

        return dataset_profile, profile
