""" define the top class for all analyzers  """
from __future__ import absolute_import, unicode_literals
import datetime
from .analyzer import Analyzer
from .utils import calculate_hash_sum, is_number
from analyzer.models import ActualColumnProfile


class AnalyzerActualColumn(Analyzer):
    def __init__(self, recordset, dataset_profile, data_types, column, row_count, index):
        super().__init__()
        self.recordset = recordset
        self.dataset_profile = dataset_profile
        self.data_types = data_types
        self.column = column
        self.row_count = row_count
        self.index = index

    def find_data_type(self):
        for data in self.data_types:
            if data[0] == self.column:
                return data[1]
        return None
    
    def _execute_session(self):
        profile = {}
        min_value = self.recordset.get_column_min(self.column)
        if is_number(min_value) or isinstance(min_value, datetime.datetime):
            profile['min'] = min_value
        else:
            profile['min'] = None

        max_value = self.recordset.get_column_max(self.column)

        if is_number(max_value) or isinstance(max_value, datetime.datetime):
            profile['max'] = max_value
        else:
            profile['max'] = None

        profile['uniqueness'] = len(self.recordset.get_column_distinct(self.column)) / self.row_count
        profile['datatype'] = self.find_data_type()
        profile['nullable'] = True
        profile['order'] = self.index

        profile['hash_sum'] = calculate_hash_sum(profile)

        ActualColumnProfile.objects.create(dataset_profile=self.dataset_profile,
                                           name=self.column,
                                           min=profile['min'],
                                           max=profile['max'],
                                           uniqueness=profile['uniqueness'],
                                           datatype=profile['datatype'],
                                           nullable=profile['nullable'],
                                           order=profile['order'],
                                           hash_sum=profile['hash_sum'])

        return profile
