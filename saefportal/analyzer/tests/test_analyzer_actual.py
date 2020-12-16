from django.test import TestCase, tag
from datetime import datetime
from utils.test_utils import load_test_db
from analyzer.analyzers.analyzer_actual_dataset import AnalyzerActualDataset
from analyzer.models import ActualDatasetProfile, ActualColumnProfile
from saef.models import DatasetSession
from .utils import make_naive


@tag("postgres")
class AnalyzerActualTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db('analyzer', 'test_analyzer_actual')

    def setUp(self):
        self.test_pk = 1
        self.dataset_session = DatasetSession.objects.get(pk=self.test_pk)

        before_act_dataset_actual_length = len(ActualDatasetProfile.objects.filter(dataset_session=self.dataset_session))
        self.assertEqual(before_act_dataset_actual_length, 0)

        analyzer = AnalyzerActualDataset(self.test_pk)
        analyzer.execute()

    def test_dataset_calculate_actual_profile_create_objects(self):
        after_act_dataset_actual = ActualDatasetProfile.objects.filter(dataset_session=self.dataset_session)
        self.assertEqual(len(after_act_dataset_actual), 1)
        self.assertEqual(len(ActualColumnProfile.objects.filter(dataset_profile=after_act_dataset_actual.first().pk)),
                         5)

    def test_dataset_calculate_actual_profile_correct_dataset_calculation(self):
        after_act_dataset_actual = ActualDatasetProfile.objects.get(dataset_session=self.dataset_session)
        self.assertEqual(after_act_dataset_actual.row_count, 4)
        self.assertEqual(after_act_dataset_actual.column_count, 5)

    def test_dataset_calculate_actual_profile_correct_column_calculation(self):
        after_act_dataset_actual = ActualDatasetProfile.objects.get(dataset_session=self.dataset_session)
        after_act_columns_actual = ActualColumnProfile.objects.filter(dataset_profile=after_act_dataset_actual.pk)
        self.assertEqual(len(after_act_columns_actual), 5)

        def assert_column_name(name, min, max, uniqueness, is_datetime=False):
            column = ActualColumnProfile.objects.get(dataset_profile=after_act_dataset_actual.pk, name=name)
            self.assertEqual(column.uniqueness, uniqueness)

            if is_datetime:
                naive_datetime_min = make_naive(column.min)
                naive_datetime_max = make_naive(column.max)
                self.assertEqual(naive_datetime_min, min)
                self.assertEqual(naive_datetime_max, max)
            else:
                self.assertEqual(column.min, min)
                self.assertEqual(column.max, max)

        assert_column_name('id', '1', '4', 1.0)
        assert_column_name('name', None, None, 1.0)
        assert_column_name('description', None, None, 1.0)
        assert_column_name('create_timestamp', datetime(2020, 4, 23, 23, 13, 59, 440000),
                           datetime(2020, 5, 30, 14, 51, 55, 485000), 1.0, True)
        assert_column_name('application_id', '2', '20', 0.5)
