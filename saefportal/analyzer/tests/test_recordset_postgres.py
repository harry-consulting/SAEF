import datetime
import json
import psycopg2
from unittest import TestCase

from django.test import tag
from analyzer.recordset.recordset_factory import recordset_factory
from saef.models import Dataset, Connection, PostgresConnection
from saefportal.settings import TEST_POSTGRES_DB_NAME, TEST_POSTGRES_USERNAME, TEST_POSTGRES_PASSWORD, TEST_POSTGRES_HOST, TEST_POSTGRES_PORT
from .utils import validate_configuration
from utils.test_utils import load_test_db
from analyzer.utilities import encrypt


@tag("postgres")
class RecordsetPostgresTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        configration = {'TEST_POSTGRES_DB_NAME': TEST_POSTGRES_DB_NAME,
                        'TEST_POSTGRES_USERNAME': TEST_POSTGRES_USERNAME,
                        'TEST_POSTGRES_PASSWORD': TEST_POSTGRES_PASSWORD,
                        'TEST_POSTGRES_HOST': TEST_POSTGRES_HOST,
                        'TEST_POSTGRES_PORT': TEST_POSTGRES_PORT}

        validate_configuration(configration)

    def setUp(self):
        self.test_schema = 'public'
        self.test_table = 'saef_job'
        self.test_column = 'id'

        load_test_db("analyzer", "test_recordset_postgres")

        dataset = Dataset.objects.get(pk=1)
        postgres_connection = PostgresConnection.objects.get(pk=1)
        postgres_connection.db_name = TEST_POSTGRES_DB_NAME
        postgres_connection.username = TEST_POSTGRES_USERNAME
        postgres_connection.password = encrypt(TEST_POSTGRES_PASSWORD)
        postgres_connection.host = TEST_POSTGRES_HOST
        postgres_connection.port = TEST_POSTGRES_PORT
        postgres_connection.save()

        self.recordset = recordset_factory(dataset)

    def test_validate_query_valid(self):
        valid, result = self.recordset.validate_query()
        self.assertEqual(valid, True)
        self.assertEqual(type(result), tuple)

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
        self.assertEqual(result, [('id', 'integer'),
                                  ('name', 'character varying'),
                                  ('description', 'character varying'),
                                  ('create_timestamp', 'timestamp with time zone'),
                                  ('application_id', 'integer')])

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
        self.assertEqual(result, [('public', 'saef_job')])

    def test_get_pk_and_unique_constraints(self):
        result = self.recordset.get_pk_and_unique_constraints(self.test_table)
        self.assertEqual(
            result, [('saef_job_pkey', 'id', 'PRIMARY KEY')])

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
                        datetime.datetime(2020, 4, 24, 1, 13, 59, 440000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                    (2, 'LoadProduct', 'Loads Production dimension',
                        datetime.datetime(2020, 4, 24, 23, 1, 7, 145000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                    (3, 'LoadSales', 'The job that loads Sales Fact',
                        datetime.datetime(2020, 4, 24, 23, 1, 33, 280000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                    (4, 'test2', 'descr for test 2',
                        datetime.datetime(2020, 5, 30, 16, 51, 55, 485000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 20)]

        self.assertEqual(result, expected)

    def test_extract_preview_limit(self):
        dataset = Dataset.objects.get(pk=1)
        dataset.dataset_access_method = 'SQL'
        dataset.dataset_extraction_sql = f'SELECT * FROM {self.test_schema}.{self.test_table} LIMIT 2'
        self.recordset = recordset_factory(dataset)

        result = self.recordset.extract_preview(300)
        expected = [['id', 'name', 'description', 'create_timestamp', 'application_id'],
                    (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                        datetime.datetime(2020, 4, 24, 1, 13, 59, 440000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                    (2, 'LoadProduct', 'Loads Production dimension',
                        datetime.datetime(2020, 4, 24, 23, 1, 7, 145000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2)]

        self.assertEqual(result, expected)

    def test_extract_schema(self):
        result = self.recordset.extract_schema(
            self.test_schema, self.test_table)
        self.assertEqual(result, [('id', 'integer', 'NO'),
                                  ('name', 'character varying', 'YES'),
                                  ('description', 'character varying', 'YES'),
                                  ('create_timestamp',
                                   'timestamp with time zone', 'YES'),
                                  ('application_id', 'integer', 'YES')])
