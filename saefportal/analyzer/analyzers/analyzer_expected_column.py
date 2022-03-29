from __future__ import absolute_import, unicode_literals
from .analyzer import Analyzer
from analyzer.models import ExpectedColumnProfile

from .util import calculate_average


class AnalyzerExpectedColumn(Analyzer):
    def __init__(self, dataset_profile, name, column):
        super().__init__()
        self.dataset_profile = dataset_profile
        self.name = name
        self.column = column

    def _execute_session(self):
        ExpectedColumnProfile.objects.create(dataset_profile=self.dataset_profile,
                                             name=self.name,
                                             min=calculate_average(self.column['min']),
                                             max=calculate_average(self.column['max']),
                                             uniqueness=calculate_average(self.column['uniqueness']),
                                             datatype=self.column['datatype'],
                                             nullable=self.column['nullable'],
                                             order=self.column['order'],
                                             hash_sum=calculate_average(self.column['hash_sum']))
