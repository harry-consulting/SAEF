import pyodbc
import datetime
from django.test import tag
from analyzer.recordset.recordset_factory import recordset_factory
from unittest import TestCase
from saefportal.settings import TEST_AZURE_DB_NAME, TEST_AZURE_USERNAME, TEST_AZURE_PASSWORD, TEST_AZURE_HOST, TEST_AZURE_PORT
from utils.test_utils import load_test_db
from .utils import validate_configuration
from saef.models import AzureConnection, Dataset
from analyzer.utilities import encrypt


@tag("azure")
class RecordsetAzureTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        configration = {'TEST_AZURE_DB_NAME': TEST_AZURE_DB_NAME,
                        'TEST_AZURE_USERNAME': TEST_AZURE_USERNAME,
                        'TEST_AZURE_PASSWORD': TEST_AZURE_PASSWORD,
                        'TEST_AZURE_HOST': TEST_AZURE_HOST,
                        'TEST_AZURE_PORT': TEST_AZURE_PORT}

        validate_configuration(configration)
        

    def setUp(self):
        self.test_schema = 'dbo'
        self.test_table = 'saef_job'
        self.test_column = 'id'

        load_test_db("analyzer", "test_recordset_azure")

        dataset = Dataset.objects.get(pk=1)
        azure_connection = AzureConnection.objects.get(pk=1)
        azure_connection.db_name = TEST_AZURE_DB_NAME
        azure_connection.username = TEST_AZURE_USERNAME
        azure_connection.password = encrypt(TEST_AZURE_PASSWORD)
        azure_connection.host = TEST_AZURE_HOST
        azure_connection.port = TEST_AZURE_PORT
        azure_connection.save()
        
        self.recordset = recordset_factory(dataset)

    def test_validate_query_valid(self):
        valid, result = self.recordset.validate_query()
        self.assertEqual(valid, True)
        self.assertEqual(type(result), pyodbc.Row)

    def test_validate_query_invalid(self):
        dataset = Dataset.objects.get(pk=1)
        dataset.dataset_access_method = 'SQL'
        dataset.dataset_extraction_sql = 'TEST'
        self.recordset = recordset_factory(dataset)

        valid, _ = self.recordset.validate_query()
        self.assertEqual(valid, False)

    def test_get_column_names(self):
        result = self.recordset.get_column_names()
        self.assertEqual(
            result, ['id', 'name', 'description', 'create_timestamp', 'application_id'])

    def test_get_row_count(self):
        result = self.recordset.get_row_count()
        self.assertEqual(result, 4)

    def test_get_column_count(self):
        result = self.recordset.get_column_count()
        self.assertEqual(result, 5)

    def test_get_column_types(self):
        result = self.recordset.get_column_types()
        self.assertEqual(result, [('id', 'int'),
                                  ('name', 'varchar'),
                                  ('description', 'varchar'),
                                  ('create_timestamp', 'datetime'),
                                  ('application_id', 'int')])

    def test_get_column_distinct(self):
        result = self.recordset.get_column_distinct(self.test_column)
        self.assertEqual(sorted(result), [1, 2, 3, 4])

    def test_get_column_min(self):
        result = self.recordset.get_column_min(self.test_column)
        self.assertEqual(result, 1)

    def test_get_column_max(self):
        result = self.recordset.get_column_max(self.test_column)
        self.assertEqual(result, 4)

    def test_get_all_tables(self):
        result = self.recordset.get_all_tables()
        self.assertEqual(result, [('dbo', 'saef_job'),
                                  ('sys', 'database_firewall_rules')])

    def test_get_pk_and_unique_constraints(self):
        result = self.recordset.get_pk_and_unique_constraints(self.test_table)
        result_clean = [(result[0][0].split('__')[1], result[0][1], result[0][2])]
        self.assertEqual(
            result_clean, [('saef_job', 'id', 'PRIMARY KEY')])

    def test_get_check_constraints(self):
        result = self.recordset.get_check_constraints(self.test_table)
        self.assertEqual(result, [])

    def test_get_is_nullable_constraints(self):
        result = self.recordset.get_is_nullable_constraints(self.test_table)
        self.assertEqual(result, [('id', 'NO'),
                                  ('name', 'YES'),
                                  ('description', 'YES'),
                                  ('create_timestamp', 'YES'),
                                  ('application_id', 'YES')])

    def test_extract_preview_no_limit(self):
        dataset = Dataset.objects.get(pk=1)
        dataset.dataset_access_method = 'SQL'
        dataset.dataset_extraction_sql = f'SELECT * FROM {self.test_schema}.{self.test_table}'
        self.recordset = recordset_factory(dataset)

        result = self.recordset.extract_preview(300)
        expected = [['id', 'name', 'description', 'create_timestamp', 'application_id'],
                    (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                     datetime.datetime(2020, 4, 23, 21, 13, 59, 440000), 2),
                    (2, 'LoadProduct', 'Loads Production dimension',
                     datetime.datetime(2020, 4, 24, 19, 1, 7, 147000), 2),
                    (3, 'LoadSales', 'The job that loads Sales Fact',
                     datetime.datetime(2020, 4, 24, 19, 1, 33, 280000), 2),
                    (4, 'test2', 'descr for test 2', datetime.datetime(2020, 5, 30, 12, 51, 55, 487000), 20)]

        self.assertEqual(result, expected)

    def test_extract_preview_limit(self):
        dataset = Dataset.objects.get(pk=1)
        dataset.dataset_access_method = 'SQL'
        dataset.dataset_extraction_sql = f'SELECT TOP 2 * FROM {self.test_schema}.{self.test_table}'
        self.recordset = recordset_factory(dataset)

        result = self.recordset.extract_preview(300)
        expected = [['id', 'name', 'description', 'create_timestamp', 'application_id'],
                    (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                     datetime.datetime(2020, 4, 23, 21, 13, 59, 440000), 2),
                    (2, 'LoadProduct', 'Loads Production dimension', datetime.datetime(2020, 4, 24, 19, 1, 7, 147000), 2)]

        self.assertEqual(result, expected)

    def test_extract_schema(self):
        result = self.recordset.extract_schema(
            self.test_schema, self.test_table)
        self.assertEqual(result, [('id', 'int', 'NO'),
                                  ('name', 'varchar', 'YES'),
                                  ('description', 'varchar', 'YES'),
                                  ('create_timestamp', 'datetime', 'YES'),
                                  ('application_id', 'int', 'YES')])
