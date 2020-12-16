from __future__ import absolute_import, unicode_literals

from saefportal.settings import COMPARISON_PROFILE_THRESHOLD
from .analyzer import Analyzer
from analyzer.models import ActualColumnProfile, ExpectedColumnProfile, RatioCount, RatioColumn
from analyzer.enums import Column


def _create_ratio_count(dataset_actual, name, actual, expected, ratio):
    RatioCount.objects.create(dataset_ratio=dataset_actual,
                              name=name,
                              expected=expected,
                              actual=actual,
                              ratio=ratio[name]['ratio'])


def _create_ratio_column(dataset_actual, name, changed_columns, ratio):
    is_change = True if len(changed_columns) != 0 else False
    RatioColumn.objects.create(dataset_ratio=dataset_actual,
                               name=name,
                               changes=is_change,
                               columns=changed_columns,
                               ratio=ratio[name]['ratio'])


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
        sum_value += column.uniqueness
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
    def __init__(self, dataset_actual, dataset_expected):
        super().__init__()
        self.dataset_actual = dataset_actual
        self.dataset_expected = dataset_expected

    def _execute_session(self):
        columns_actual = ActualColumnProfile.objects.filter(dataset_profile_id=self.dataset_actual.pk)
        columns_expected = ExpectedColumnProfile.objects.filter(dataset_profile_id=self.dataset_expected.pk)

        ratio = {'row_count_ratio': _ratio_difference_abs(self.dataset_actual.row_count,
                                                          self.dataset_expected.row_count),
                 'column_count_ratio': _ratio_difference_abs(self.dataset_actual.column_count,
                                                             self.dataset_expected.column_count)}

        columns_actual_definitions, columns_expected_definitions = _retrieve_column_definitions(columns_actual,
                                                                                                columns_expected)
        added_columns, deleted_columns, changed_order_columns = _column_change(columns_actual_definitions,
                                                                               columns_expected_definitions,
                                                                               Column.ORDER.value,
                                                                               False)

        ratio['column_order_ratio'] = _ratio_difference(changed_order_columns,
                                                        self.dataset_expected.column_count)

        ratio['column_deleted_ratio'] = _ratio_difference(deleted_columns,
                                                          self.dataset_expected.column_count)

        ratio['column_added_ratio'] = _ratio_difference(added_columns,
                                                        self.dataset_expected.column_count)

        _, _, changed_datatype_columns = _column_change(columns_actual_definitions,
                                                        columns_expected_definitions,
                                                        Column.TYPE.value)

        ratio['column_datatype_ratio'] = _ratio_difference(changed_datatype_columns,
                                                           self.dataset_expected.column_count)

        actual_uniqueness_sum = _columns_sum_uniqueness(columns_actual)
        expected_uniqueness_sum = _columns_sum_uniqueness(columns_expected)
        ratio['column_uniqueness_ratio'] = _ratio_difference_abs(actual_uniqueness_sum, expected_uniqueness_sum)

        ratio['degree_of_change'] = _calculate_change(ratio)
        self.dataset_actual.dataset_session.degree_of_change = ratio['degree_of_change']
        self.dataset_actual.dataset_session.save()

        _create_ratio_count(self.dataset_actual, 'row_count_ratio',
                            self.dataset_actual.row_count,
                            self.dataset_expected.row_count,
                            ratio)

        _create_ratio_count(self.dataset_actual, 'column_count_ratio',
                            self.dataset_actual.column_count,
                            self.dataset_expected.column_count,
                            ratio)

        _create_ratio_column(self.dataset_actual, 'column_order_ratio', changed_order_columns, ratio)
        _create_ratio_column(self.dataset_actual, 'column_deleted_ratio', deleted_columns, ratio)
        _create_ratio_column(self.dataset_actual, 'column_added_ratio', added_columns, ratio)
        _create_ratio_column(self.dataset_actual, 'column_datatype_ratio', changed_datatype_columns, ratio)

        _create_ratio_count(self.dataset_actual,
                            'column_uniqueness_ratio',
                            actual_uniqueness_sum,
                            expected_uniqueness_sum,
                            ratio)

        return ratio
