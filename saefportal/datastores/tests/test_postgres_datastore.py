import pandas as pd
from decouple import config
from django.test import TestCase
from model_bakery import baker


class PostgresDatastoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                                   username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                                   password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

    def test_valid_connection(self):
        result = self.datastore.is_connection_valid()
        self.assertTrue(result)

    def test_invalid_connection(self):
        self.datastore._connection_string["host"] = "invalid host"

        result = self.datastore.is_connection_valid()
        self.assertFalse(result)

        self.datastore._connection_string["host"] = config("TEST_POSTGRES_HOST")

    def test_get_viable_datasets(self):
        result = self.datastore.get_viable_datasets()

        human_resources_tables = result["Tables"]["humanresources"]
        self.assertIn({"value": "humanresources.employee", "display": "employee"}, human_resources_tables)
        self.assertIn({"value": "humanresources.jobcandidate", "display": "jobcandidate"}, human_resources_tables)

        human_resources_views = result["Views"]["humanresources"]
        self.assertIn({"value": "humanresources.vemployee", "display": "vemployee"}, human_resources_views)
        self.assertIn({"value": "humanresources.vjobcandidate", "display": "vjobcandidate"}, human_resources_views)

    def test_retrieve_data(self):
        result = self.datastore.retrieve_data(query="SELECT shiftid, name FROM humanresources.shift")

        df = pd.DataFrame(columns=["shiftid", "name"], data=[[1, "Day"], [2, "Evening"], [3, "Night"]])
        self.assertTrue(df.equals(result))

    def test_retrieve_data_limit(self):
        result = self.datastore.retrieve_data(query="SELECT shiftid, name FROM humanresources.shift", limit=1)

        df = pd.DataFrame(columns=["shiftid", "name"], data=[[1, "Day"]])
        self.assertTrue(df.equals(result))
