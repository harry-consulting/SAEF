import pandas as pd
from decouple import config
from django.test import TestCase
from model_bakery import baker


class AzureDatastoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.datastore = baker.make("datastores.AzureDatastore", database_name=config("TEST_AZURE_DATABASE_NAME"),
                                   username=config("TEST_AZURE_USERNAME"), password=config("TEST_AZURE_PASSWORD"),
                                   host=config("TEST_AZURE_HOST"), port=config("TEST_AZURE_PORT"))

    def test_valid_connection(self):
        result = self.datastore.is_connection_valid()
        self.assertTrue(result)

    def test_invalid_connection(self):
        valid_connection_string = self.datastore._connection_string
        self.datastore._connection_string = "invalid connection string"

        result = self.datastore.is_connection_valid()
        self.assertFalse(result)

        self.datastore._connection_string = valid_connection_string

    def test_get_viable_datasets(self):
        result = self.datastore.get_viable_datasets()

        self.assertIn({"value": "SalesLT.Address", "display": "Address"}, result["Tables"]["SalesLT"])
        self.assertIn({"value": "tmp.nycsales", "display": "nycsales"}, result["Tables"]["tmp"])

        self.assertIn({"value": "dbo.t123", "display": "t123"}, result["Views"]["dbo"])
        self.assertIn({"value": "SalesLT.vGetAllCategories", "display": "vGetAllCategories"},
                      result["Views"]["SalesLT"])

    def test_retrieve_data(self):
        result = self.datastore.retrieve_data(query="SELECT AddressID, City FROM SalesLT.Address WHERE City = 'Dallas'")

        df = pd.DataFrame(columns=["AddressID", "City"], data=[[577, "Dallas"], [25, "Dallas"], [588, "Dallas"],
                                                               [572, "Dallas"], [581, "Dallas"], [574, "Dallas"]])
        self.assertTrue(df.equals(result))

    def test_retrieve_data_limit(self):
        result = self.datastore.retrieve_data(query="SELECT AddressID, City FROM SalesLT.Address WHERE City = 'Dallas'",
                                              limit=1)

        df = pd.DataFrame(columns=["AddressID", "City"], data=[[577, "Dallas"]])
        self.assertTrue(df.equals(result))
