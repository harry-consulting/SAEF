import pyodbc
import datetime
from django.test import tag
from analyzer.datastore.datastore_factory import datastore_factory
from unittest import TestCase

from utils.test_utils import load_test_db
from saefportal.settings import TEST_AZURE_DB_NAME, TEST_AZURE_USERNAME, TEST_AZURE_PASSWORD, TEST_AZURE_HOST, \
    TEST_AZURE_PORT
from saef.models import Dataset, AzureConnection
from analyzer.tests.utils import validate_configuration
from analyzer.utilities import encrypt


@tag("azure")
class DatastoreAzureTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        configuration = {'TEST_AZURE_DB_NAME': TEST_AZURE_DB_NAME,
                         'TEST_AZURE_USERNAME': TEST_AZURE_USERNAME,
                         'TEST_AZURE_PASSWORD': TEST_AZURE_PASSWORD,
                         'TEST_AZURE_HOST': TEST_AZURE_HOST,
                         'TEST_AZURE_PORT': TEST_AZURE_PORT}

        validate_configuration(configuration)

    def setUp(self):
        load_test_db("analyzer", "test_datastore_azure")

        dataset = Dataset.objects.get(pk=1)
        azure_connection = AzureConnection.objects.get(pk=1)
        azure_connection.db_name = TEST_AZURE_DB_NAME
        azure_connection.username = TEST_AZURE_USERNAME
        azure_connection.password = encrypt(TEST_AZURE_PASSWORD)
        azure_connection.host = TEST_AZURE_HOST
        azure_connection.port = TEST_AZURE_PORT
        azure_connection.save()

        self.datastore = datastore_factory(dataset.connection.pk)
        self.setup_test_database()

    def setup_test_database(self):
        result = self.datastore.execute_query('SELECT * FROM saef_job')

        if result:
            return

        self.datastore.execute_query("""
                        CREATE TABLE saef_job 
                        (id INTEGER PRIMARY KEY, 
                        name VARCHAR(255), 
                        description VARCHAR(255),
                        create_timestamp datetime, 
                        application_id INTEGER)""")

        self.datastore.execute_query("""
                    INSERT INTO saef_job
                    VALUES
                        ( 1, 'LoadDimCustomer', 'Customer dimension from source tables', '2020-04-23T21:13:59.440', 2 ),
                        ( 2, 'LoadProduct', 'Loads Production dimension', '2020-04-24T19:01:07.145', 2 ),
                        ( 3, 'LoadSales', 'The job that loads Sales Fact', '2020-04-24T19:01:33.280', 2 ),
                        ( 4, 'test2', 'descr for test 2', '2020-05-30T12:51:55.485', 20 )
                    """)

    def test_execute_query_valid(self):
        result = self.datastore.execute_query('SELECT 1')
        self.assertEqual(True, result)

    def test_execute_query_invalid(self):
        result = self.datastore.execute_query('invalid')
        self.assertEqual(bool, type(result))

    def test_fetch_one_without_column_name(self):
        result = self.datastore.fetch_one('SELECT TOP 2 * FROM saef_job')
        self.assertEqual(tuple(result), (1, 'LoadDimCustomer', 'Customer dimension from source tables',
                                         datetime.datetime(2020, 4, 23, 21, 13, 59, 440000), 2))

    def test_fetch_one_with_column_name(self):
        result = self.datastore.fetch_one(
            'SELECT TOP 2 * FROM saef_job', get_column_names=True)
        self.assertEqual(
            result, ['id', 'name', 'description', 'create_timestamp', 'application_id'])

    def test_fetch_one_error(self):
        result = self.datastore.fetch_one('SELECT TEST')
        self.assertEqual(pyodbc.ProgrammingError, type(result))

    def test_fetch_all_without_column_name(self):
        result = self.datastore.fetch_all('SELECT TOP 2 * FROM saef_job')
        self.assertEqual(result, [(1, 'LoadDimCustomer', 'Customer dimension from source tables',
                                   datetime.datetime(2020, 4, 23, 21, 13, 59, 440000), 2),
                                  (2, 'LoadProduct', 'Loads Production dimension',
                                   datetime.datetime(2020, 4, 24, 19, 1, 7, 147000), 2)])

    def test_fetch_all_with_column_name(self):
        result = self.datastore.fetch_all(
            'SELECT TOP 2 * FROM saef_job', get_column_names=True)
        self.assertEqual(result, [['id', 'name', 'description', 'create_timestamp', 'application_id'],
                                  (1, 'LoadDimCustomer', 'Customer dimension from source tables', datetime.datetime(
                                      2020, 4, 23, 21, 13, 59, 440000), 2),
                                  (2, 'LoadProduct', 'Loads Production dimension',
                                   datetime.datetime(2020, 4, 24, 19, 1, 7, 147000), 2)])

    def test_fetch_all_error(self):
        result = self.datastore.fetch_all('SELECT TEST')
        self.assertEqual(type(result), pyodbc.ProgrammingError)
