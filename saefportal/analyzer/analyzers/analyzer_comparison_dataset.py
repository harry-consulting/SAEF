from __future__ import absolute_import, unicode_literals

from saefportal.settings import COMPARISON_PROFILE_THRESHOLD
from .analyzer import Analyzer
from analyzer.models import ActualColumnProfile, ExpectedColumnProfile
from analyzer.enums import Column


def _calculate_change(ratio):
    result = 0
    for value in ratio.values():
        result += value['ratio'] * COMPARISON_PROFILE_THRESHOLD

    return result / len(ratio)


def _retrieve_column_definitions(columns_actual, columns_expected):
    columns_actual_definitions = {}
    columns_expected_definitions = {}

    for actual_column in columns_actual:
        columns_actual_definitions[actual_column.name] = (
            actual_column.datatype, actual_column.nullable, actual_column.order)

    for expected_column in columns_expected:
        columns_expected_definitions[expected_column.name] = (
            expected_column.datatype, expected_column.nullable, expected_column.order)

    return columns_actual_definitions, columns_expected_definitions


def _column_change(columns_actual, columns_expected, value, ignore_deleted=True):
    column_dict = {'added': [], 'deleted': [], 'changes': []}

    for name, actual_column in columns_actual.items():
        if name not in columns_expected:
            column_dict['added'].append(name)
        elif actual_column[value] != columns_expected[name][value]:
            column_dict['changes'].append(name)

    if not ignore_deleted:
        for name in columns_expected.keys():
            if name not in columns_actual:
                column_dict['deleted'].append(name)

    return column_dict['added'], column_dict['deleted'], column_dict['changes']


def _columns_sum_uniqueness(columns):
    sum_value = 0
    for column in columns:
        sum_value += column.uniqueness if column.uniqueness else 0
    return sum_value


def _ratio_difference_abs(actual, expected):
    if expected == 0:
        return {'actual': actual, 'expected': expected, 'ratio': 0}

    ratio = abs(actual - expected) / expected

    return {'actual': actual, 'expected': expected, 'ratio': ratio}


def _ratio_difference(columns, denominator):
    ratio = len(columns) / denominator
    is_change = True if len(columns) != 0 else False

    return {'changes': is_change, 'columns': columns, 'ratio': ratio}


class AnalyzerComparisonDataset(Analyzer):
    def __init__(self, actual_dataset_profile, expected_dataset_profile):
        super().__init__()
        self.actual_dataset_profile = actual_dataset_profile
        self.expected_dataset_profile = expected_dataset_profile

    def _execute_session(self):
        columns_actual = ActualColumnProfile.objects.filter(dataset_profile_id=self.actual_dataset_profile.pk)
        columns_expected = ExpectedColumnProfile.objects.filter(dataset_profile_id=self.expected_dataset_profile.pk)

        ratio = {'row_count_ratio': _ratio_difference_abs(self.actual_dataset_profile.row_count,
                                                          self.expected_dataset_profile.row_count),
                 'column_count_ratio': _ratio_difference_abs(self.actual_dataset_profile.column_count,
                                                             self.expected_dataset_profile.column_count)}

        columns_actual_definitions, columns_expected_definitions = _retrieve_column_definitions(columns_actual,
                                                                                                columns_expected)
        added_columns, deleted_columns, changed_order_columns = _column_change(columns_actual_definitions,
                                                                               columns_expected_definitions,
                                                                               Column.ORDER.value,
                                                                               False)

        ratio['column_order_ratio'] = _ratio_difference(changed_order_columns,
                                                        self.expected_dataset_profile.column_count)

        ratio['column_deleted_ratio'] = _ratio_difference(deleted_columns,
                                                          self.expected_dataset_profile.column_count)

        ratio['column_added_ratio'] = _ratio_difference(added_columns,
                                                        self.expected_dataset_profile.column_count)

        _, _, changed_datatype_columns = _column_change(columns_actual_definitions,
                                                        columns_expected_definitions,
                                                        Column.TYPE.value)

        ratio['column_datatype_ratio'] = _ratio_difference(changed_datatype_columns,
                                                           self.expected_dataset_profile.column_count)

        actual_uniqueness_sum = _columns_sum_uniqueness(columns_actual)
        expected_uniqueness_sum = _columns_sum_uniqueness(columns_expected)
        ratio['column_uniqueness_ratio'] = _ratio_difference_abs(actual_uniqueness_sum, expected_uniqueness_sum)

        ratio['degree_of_change'] = _calculate_change(ratio)
        self.actual_dataset_profile.dataset_run.result = {"degree_of_change": ratio['degree_of_change']}
        self.actual_dataset_profile.dataset_run.save()

        return ratio
