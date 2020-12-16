from unittest import TestCase

from saef.models import Dataset
from analyzer.recordset.recordset_factory import recordset_factory
from utils.test_utils import load_test_dataset


class RecordsetFactoryTests(TestCase):
    def test_get_postgres_class(self):
        load_test_dataset()
        dataset = Dataset.objects.get(pk=11)
        test_instance = recordset_factory(dataset)
        self.assertEqual(type(test_instance).__name__, "RecordsetPostgres")
