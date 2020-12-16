import datetime
import psycopg2
from analyzer.datastore.datastore_factory import datastore_factory
from unittest import TestCase

from django.test import tag
from utils.test_utils import load_test_db
from .utils import validate_configuration
from analyzer.utilities import encrypt

from saef.models import Dataset, PostgresConnection
from saefportal.settings import TEST_POSTGRES_DB_NAME, TEST_POSTGRES_USERNAME, TEST_POSTGRES_PASSWORD, TEST_POSTGRES_HOST, TEST_POSTGRES_PORT


@tag("postgres")
class DatastorePostgresTests(TestCase):
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
        load_test_db("analyzer", "test_datastore_postgres")

        dataset = Dataset.objects.get(pk=1)
        postgres_connection = PostgresConnection.objects.get(pk=1)
        postgres_connection.db_name = TEST_POSTGRES_DB_NAME
        postgres_connection.username = TEST_POSTGRES_USERNAME
        postgres_connection.password = encrypt(TEST_POSTGRES_PASSWORD)
        postgres_connection.host = TEST_POSTGRES_HOST
        postgres_connection.port = TEST_POSTGRES_PORT
        postgres_connection.save()

        self.datastore = datastore_factory(dataset.connection.pk)

    def test_execute_query_valid(self):
        result = self.datastore.execute_query('SELECT 1')
        self.assertEqual(True, result)

    def test_execute_query_invalid(self):
        result = self.datastore.execute_query('invalid')
        self.assertEqual(bool, type(result))

    def test_fetch_one_without_column_name(self):
        result = self.datastore.fetch_one('SELECT * FROM saef_job LIMIT 2')
        self.assertEqual(tuple(result), (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                                         datetime.datetime(2020, 4, 24, 1, 13, 59, 440000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2))

    def test_fetch_one_with_column_name(self):
        result = self.datastore.fetch_one(
            'SELECT * FROM saef_job LIMIT 2', get_column_names=True)
        self.assertEqual(
            result, ['id', 'name', 'description', 'create_timestamp', 'application_id'])

    def test_fetch_one_error(self):
        result = self.datastore.fetch_one('SELECT TEST')
        self.assertEqual(type(result), psycopg2.errors.UndefinedColumn)

    def test_fetch_all_without_column_name(self):
        result = self.datastore.fetch_all('SELECT * FROM saef_job LIMIT 2')
        self.assertEqual(result, [(1, 'LoadDimCustomer', 'Customer dimension from source tables',
                                   datetime.datetime(2020, 4, 24, 1, 13, 59, 440000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                                  (2, 'LoadProduct', 'Loads Production dimension',
                                   datetime.datetime(2020, 4, 24, 23, 1, 7, 145000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2)])

    def test_fetch_all_with_column_name(self):
        result = self.datastore.fetch_all(
            'SELECT * FROM saef_job LIMIT 2', get_column_names=True)
        self.assertEqual(result, [['id', 'name', 'description', 'create_timestamp', 'application_id'],
                                  (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                                   datetime.datetime(2020, 4, 24, 1, 13, 59, 440000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2),
                                  (2, 'LoadProduct', 'Loads Production dimension',
                                   datetime.datetime(2020, 4, 24, 23, 1, 7, 145000, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 2)])

    def test_fetch_all_error(self):
        result = self.datastore.fetch_all('SELECT TEST')
        self.assertEqual(type(result), psycopg2.errors.UndefinedColumn)
