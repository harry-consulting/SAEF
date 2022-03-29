from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from analyzer.models import ActualColumnProfile, ActualDatasetProfile, ExpectedDatasetProfile
from .analyzer import Analyzer
from .analyzer_expected_column import AnalyzerExpectedColumn
from .util import add_value, calculate_average
from saefportal.settings import EXPECTED_DATASET_COLUMN_DEFINITION_THRESHOLD
from settings.models import Settings


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
        profile['column'][name] = defaultdict(list)

    return profile['column'][name]


class AnalyzerExpectedDataset(Analyzer):
    def __init__(self, dataset_run, actual_dataset_profile):
        super().__init__()
        self.dataset_run = dataset_run
        self.actual_dataset_profile = actual_dataset_profile

    def _execute_session(self):
        settings = Settings.objects.get()

        dataset_profiles = ActualDatasetProfile.objects.filter(dataset_run__dataset=self.dataset_run.dataset)
        dataset_profiles = dataset_profiles.order_by('-pk')[:settings.profile_expected_datasets_n]

        if len(dataset_profiles) == 0:
            return None

        profile = {'row_count': [], 'column_count': [], 'column_definitions': [], 'hash_sum': [], 'column': {}}

        for dataset_profile in dataset_profiles:
            profile['row_count'].append(dataset_profile.row_count)
            profile['column_count'].append(dataset_profile.column_count)
            profile['hash_sum'].append(dataset_profile.hash_sum)

            column_profiles = ActualColumnProfile.objects.filter(dataset_profile=dataset_profile.id)

            column_definitions = []

            for column_profile in column_profiles:
                column = initialize_column_profile(profile, column_profile.name)

                # Attributes used for average calculation
                column['min'] = add_value(column['min'], column_profile.min)
                column['max'] = add_value(column['max'], column_profile.max)
                column['uniqueness'].append(column_profile.uniqueness)
                column['hash_sum'].append(column_profile.hash_sum)

                # Attributes information
                column['datatype'] = column_profile.datatype
                column['nullable'] = column_profile.nullable
                column['order'] = column_profile.order

                column_definitions.append((column_profile.name, column_profile.datatype, column_profile.nullable,
                                           column_profile.order))

            profile['column_definitions'].append(column_definitions)

        expected_dataset_profile = ExpectedDatasetProfile.objects.create(
            actual_dataset_profile=self.actual_dataset_profile,
            row_count=calculate_average(profile['row_count']),
            column_count=calculate_average(profile['column_count']),
            hash_sum=calculate_average(profile['hash_sum']))

        common_column_definitions = retrieve_most_common_column_definitions(profile['column_definitions'])

        for column_profile in common_column_definitions:
            column = profile['column'][column_profile[0]]
            analyzer = AnalyzerExpectedColumn(expected_dataset_profile, column_profile[0], column)
            analyzer.execute()

        return expected_dataset_profile
