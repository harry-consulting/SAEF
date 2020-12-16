from datetime import datetime
from django.test import TestCase

from utils.test_utils import load_test_db
from analyzer.analyzers.analyzer_expected_dataset import AnalyzerExpectedDataset
from saef.models import DatasetSession

from analyzer.models import ActualDatasetProfile, ExpectedDatasetProfile, ExpectedColumnProfile
from .utils import make_naive


class AnalyzerExpectedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db('analyzer', 'test_analyzer_expected')

    def setUp(self):
        self.test_pk = 1
        self.dataset_session = DatasetSession.objects.get(pk=self.test_pk)
        self.actual_dataset_profile = ActualDatasetProfile.objects.get(dataset_session=self.dataset_session)
        before_act_dataset_expected_length = len(ExpectedDatasetProfile.objects.filter(actual_dataset_profile=self.actual_dataset_profile))
        self.assertEqual(before_act_dataset_expected_length, 0)

        analyzer = AnalyzerExpectedDataset(1, self.actual_dataset_profile)
        analyzer.execute()

    def test_dataset_calculate_expected_profile_create_objects(self):
        after_act_dataset_expected = ExpectedDatasetProfile.objects.filter(actual_dataset_profile=self.actual_dataset_profile)
        self.assertEqual(len(after_act_dataset_expected), 1)
        self.assertEqual(
            len(ExpectedColumnProfile.objects.filter(dataset_profile=after_act_dataset_expected.first().pk)), 4)

    def test_dataset_calculate_expected_profile_correct_dataset_calculation(self):
        after_act_dataset_expected = ExpectedDatasetProfile.objects.get(actual_dataset_profile=self.actual_dataset_profile)
        self.assertEqual(after_act_dataset_expected.row_count, 3)
        self.assertEqual(after_act_dataset_expected.column_count, 4.8)

    def test_dataset_calculate_expected_profile_correct_column_calculation(self):
        after_act_dataset_expected = ExpectedDatasetProfile.objects.get(actual_dataset_profile=self.actual_dataset_profile)
        after_act_columns_expected = ExpectedColumnProfile.objects.filter(dataset_profile=after_act_dataset_expected.pk)
        self.assertEqual(len(after_act_columns_expected), 4)

        def assert_column_name(name, min, max, uniqueness, is_datetime=False):
            column = ExpectedColumnProfile.objects.get(dataset_profile=after_act_dataset_expected.pk, name=name)
            self.assertEqual(column.uniqueness, uniqueness)

            if is_datetime:
                naive_datetime_min = make_naive(column.min)
                naive_datetime_max = make_naive(column.max)
                self.assertEqual(naive_datetime_min, min)
                self.assertEqual(naive_datetime_max, max)
            else:
                self.assertEqual(column.min, min)
                self.assertEqual(column.max, max)

        assert_column_name('id', '1.5', '7.5', 0.75)
        assert_column_name('description', None, None, 0.75)
        assert_column_name('create_timestamp',
                           datetime(2020, 4, 27, 9, 13, 59, 440000),
                           datetime(2020, 5, 30, 14, 51, 55, 485000), 
                           0.75, 
                           True)
        assert_column_name('application_id', '3.0', '30.0', 0.75)
