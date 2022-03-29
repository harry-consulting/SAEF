from __future__ import absolute_import, unicode_literals

import datetime

from analyzer.models import ActualColumnProfile
from .analyzer import Analyzer
from .util import calculate_hash_sum, is_number


class AnalyzerActualColumn(Analyzer):
    def __init__(self, data_df, column_types, dataset_profile, column, row_count, index):
        super().__init__()
        self.data_df = data_df
        self.column_types = column_types
        self.dataset_profile = dataset_profile
        self.column = column
        self.row_count = row_count
        self.index = index
    
    def _execute_session(self):
        profile = {}

        try:
            min_value = self.data_df[self.column].min()
        except TypeError:
            min_value = self.data_df[self.column].astype(str).min()

        try:
            max_value = self.data_df[self.column].max()
        except TypeError:
            max_value = self.data_df[self.column].astype(str).max()

        profile["min"] = min_value if is_number(min_value) or isinstance(min_value, datetime.datetime) else None
        profile["max"] = max_value if is_number(max_value) or isinstance(max_value, datetime.datetime) else None
        profile["uniqueness"] = len(self.data_df[self.column].unique()) / self.row_count
        profile["datatype"] = self.column_types[self.column]
        profile["order"] = self.index
        profile["hash_sum"] = calculate_hash_sum(profile)
        profile["nullable"] = True

        ActualColumnProfile.objects.create(dataset_profile=self.dataset_profile, name=self.column, min=profile["min"],
                                           max=profile["max"], uniqueness=profile["uniqueness"],
                                           datatype=profile["datatype"], nullable=profile["nullable"],
                                           order=profile["order"], hash_sum=profile["hash_sum"])

        return profile
