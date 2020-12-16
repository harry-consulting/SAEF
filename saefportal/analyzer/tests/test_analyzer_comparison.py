from django.test import TestCase

from utils.test_utils import load_test_db
from analyzer.analyzers.analyzer_comparison_dataset import AnalyzerComparisonDataset

from analyzer.models import ActualDatasetProfile, ExpectedDatasetProfile, RatioCount, RatioColumn
from saef.models import DatasetSession


class AnalyzerComparisonTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_db("analyzer", "test_analyzer_comparison")

    def setUp(self):
        self.test_pk = 1

        self.dataset_session = DatasetSession.objects.filter(pk=self.test_pk).first()
        self.dataset_actual = ActualDatasetProfile.objects.filter(dataset_session=self.dataset_session).first()
        self.dataset_expected = ExpectedDatasetProfile.objects.filter(actual_dataset_profile=self.dataset_actual).first()

        self.assertIsNone(self.dataset_actual.dataset_session.degree_of_change)

        analyzer = AnalyzerComparisonDataset(self.dataset_actual, self.dataset_expected)
        analyzer.execute()

    def test_dataset_calculate_comparison_create_objects(self):
        self.assertEqual(self.dataset_actual.dataset_session.degree_of_change, 0.1857142857142857)
        self.assertEqual(len(RatioCount.objects.filter(dataset_ratio=self.dataset_actual.pk)), 3)
        self.assertEqual(len(RatioColumn.objects.filter(dataset_ratio=self.dataset_actual.pk)), 4)

    def test_dataset_calculate_comparison_profile(self):
        self.assertEqual(self.dataset_actual.dataset_session.degree_of_change, 0.1857142857142857)

        def assert_ratio_count(name, actual, expected, ratio):
            column = RatioCount.objects.get(dataset_ratio=self.dataset_actual.pk, name=name)
            self.assertEqual(column.name, name)
            self.assertEqual(column.actual, actual)
            self.assertEqual(column.expected, expected)
            self.assertEqual(column.ratio, ratio)

        def assert_ratio_column(name, changes, columns, ratio):
            column = RatioColumn.objects.get(dataset_ratio=self.dataset_actual.pk, name=name)
            self.assertEqual(column.changes, changes)
            self.assertEqual(column.columns, columns)
            self.assertEqual(column.ratio, ratio)

        assert_ratio_count('row_count_ratio', 4, 6, 0.3333333333333333)
        assert_ratio_count('column_count_ratio', 5, 7.5, 0.3333333333333333)

        assert_ratio_column('column_order_ratio', False, [], 0.0)
        assert_ratio_column('column_deleted_ratio', False, [], 0.0)
        assert_ratio_column('column_added_ratio', True, ['name'], 0.13333333333333333)
        assert_ratio_column('column_datatype_ratio', False, [], 0.0)

        assert_ratio_count('column_uniqueness_ratio', 4.5, 3, 0.5)
