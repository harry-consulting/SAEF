from __future__ import absolute_import, unicode_literals
from analyzer.recordset.recordset_factory import recordset_factory
from saef.models import DatasetSession
from .analyzer import Analyzer
from analyzer.models import ActualDatasetProfile

from .utils import calculate_hash_sum
from .analyzer_actual_column import AnalyzerActualColumn


class AnalyzerActualDataset(Analyzer):
    def __init__(self, dataset_session_pk):
        super().__init__()
        self.dataset_session_pk = dataset_session_pk

    def _execute_session(self):
        dataset_session = DatasetSession.objects.get(pk=self.dataset_session_pk)
        self.recordset = recordset_factory(dataset_session.dataset)
        valid, result = self.recordset.validate_query()
        if not valid:
            raise result

        profile = {
            'column': {},
            'row_count': self.recordset.get_row_count(),
            'column_count': self.recordset.get_column_count()
        }

        columns = self.recordset.get_column_names()

        dataset_profile = ActualDatasetProfile.objects.create(dataset_session=dataset_session,
                                                              row_count=profile['row_count'],
                                                              column_count=profile['column_count'])
        datatypes = self.recordset.get_column_types()
        for index, column in enumerate(columns):
            analyzer = AnalyzerActualColumn(self.recordset,
                                            dataset_profile,
                                            datatypes,
                                            column,
                                            profile['row_count'],
                                            index)
            profile['column'][column] = analyzer.execute()

        profile['hash_sum'] = calculate_hash_sum(profile)

        dataset_profile.hash_sum = profile['hash_sum']
        dataset_profile.save()

        return dataset_profile, profile
