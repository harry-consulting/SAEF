import json

from decouple import config
from django.urls import reverse
from model_bakery import baker

from datasets.models import Connection
from datastores.models import PostgresDatastore
from util.test_util import ClientLoginDatalakeTestCase


class ConnectionTests(ClientLoginDatalakeTestCase):
    def setUp(self):
        super(ConnectionTests, self).setUp()

        self.connection = baker.make("datasets.Connection", name="test connection", owner=self.user)
        self.form_data = {"name": "postgres", "type": "POSTGRES", "host": config("TEST_POSTGRES_HOST"),
                          "database_name": config("TEST_POSTGRES_DATABASE_NAME"), "owner": self.user.id,
                          "username": config("TEST_POSTGRES_USERNAME"), "port": config("TEST_POSTGRES_PORT"),
                          "password": config("TEST_POSTGRES_PASSWORD")}

    def test_create_connection(self):
        """When a connection is created using the view, it should be shown in the index navbar."""
        response = self.client.post(reverse("datasets:create_connection"), self.form_data, follow=True)

        self.assertContains(response, "postgres")
        self.assertTrue(Connection.objects.filter(name="postgres").exists())
        self.assertTrue(PostgresDatastore.objects.filter(host=config("TEST_POSTGRES_HOST")).exists())

    def test_update_connection(self):
        """When a connection is updated using the view, the updated connection should be shown in the index navbar."""
        self.assertTrue(Connection.objects.filter(title="test connection").exists())
        form_data = {"title": "updated test connection", "owner": self.user.id}

        url = reverse("datasets:update_connection", kwargs={"pk": self.connection.id})
        response = self.client.post(url, form_data, follow=True)

        self.assertContains(response, "updated test connection")
        self.assertTrue(Connection.objects.filter(title="updated test connection").exists())

    def test_delete_connection(self):
        """When a connection is deleted using the view, it should be removed from the index navbar."""
        url = reverse("datasets:delete_connection", kwargs={"pk": self.connection.id})
        response = self.client.post(url, follow=True)

        self.assertQuerysetEqual(response.context["connections"], [])
        self.assertFalse(Connection.objects.filter(name="test connection").exists())

    def test_test_valid_connection(self):
        response = self.client.post(reverse("datasets:test_connection"), self.form_data)

        self.assertTrue(json.loads(response.content)["connection_valid"])

    def test_test_invalid_connection(self):
        self.form_data["host"] = "invalid host"
        response = self.client.post(reverse("datasets:test_connection"), self.form_data)

        self.assertFalse(json.loads(response.content)["connection_valid"])

    def test_filename_validator(self):
        """Connections should not be able to be created with a name that cannot be a filename."""
        self.form_data["name"] = "invalid / name:"
        response = self.client.post(reverse("datasets:create_connection"), self.form_data, follow=True)

        self.assertContains(response, "Name cannot be used as a folder name in the datalake.")
        self.assertFalse(Connection.objects.filter(name="invalid / name:").exists())
