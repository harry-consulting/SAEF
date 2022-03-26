from decouple import config
from django.urls import reverse
from model_bakery import baker

from datasets.forms import QueryDatasetModelForm, ImportDatasetsModelForm
from datasets.models import Dataset
from util.test_util import ClientLoginDatalakeTestCase


class DatasetTests(ClientLoginDatalakeTestCase):
    @classmethod
    def setUpTestData(cls):
        super(DatasetTests, cls).setUpTestData()

        cls.datastore = baker.make("datastores.PostgresDatastore", database_name=config("TEST_POSTGRES_DATABASE_NAME"),
                                   username=config("TEST_POSTGRES_USERNAME"), host=config("TEST_POSTGRES_HOST"),
                                   password=config("TEST_POSTGRES_PASSWORD"), port=config("TEST_POSTGRES_PORT"))

        cls.connection = baker.make("datasets.Connection", name="owned connection", owner=cls.user,
                                    datastore=cls.datastore)

    def test_create_query_dataset(self):
        """If a query dataset is created using the view, it should be shown in the index navbar."""
        form_data = {"name": "test dataset", "query": "SELECT * FROM humanresources.employee",
                     "connection": self.connection.id, "owner": self.user.id, "type": "QUERY"}
        response = self.client.post(reverse("datasets:create_query_dataset"), form_data, follow=True)

        self.assertContains(response, "test dataset")
        self.assertContains(response, "jobtitle")
        self.assertTrue(Dataset.objects.filter(name="test dataset").exists())

    def test_create_query_dataset_viable_connections(self):
        """When creating a query dataset, the only viable connections should be those the user has permission for."""
        unowned_connection = baker.make("datasets.Connection", name="unowned connection")
        form = QueryDatasetModelForm(user=self.user)

        self.assertTrue(form.fields["connection"].queryset.filter(id=self.connection.id).exists())
        self.assertFalse(form.fields["connection"].queryset.filter(id=unowned_connection.id).exists())

    def test_test_valid_query(self):
        """If a valid query is tested, it should return the column names and query result."""
        data = {"connection_id": self.connection.id, "query": "SELECT * FROM humanresources.employee"}
        response = self.client.post(reverse("datasets:query_preview"), data)

        self.assertTrue(response.context["query_valid"])
        self.assertContains(response, "Query preview")
        self.assertContains(response, "jobtitle")

    def test_test_invalid_query(self):
        """If an invalid query is tested, it should return that the query is invalid."""
        data = {"connection_id": self.connection.id, "query": "invalid query"}
        response = self.client.post(reverse("datasets:query_preview"), data)

        self.assertFalse(response.context["query_valid"])

    def test_import_datasets(self):
        """If multiple datasets, both tables and views, are imported, they should be shown in the index navbar."""
        datasets = ["Tables.humanresources.employee", "Views.humanresources.vemployeedepartment"]

        form_data = {"dataset-select": datasets, "connection": self.connection.id, "owner": self.user.id}
        self.client.post(reverse("datasets:import_datasets"), form_data)

        response = self.client.get(reverse("datasets:index"))

        self.assertContains(response, "humanresources.employee")
        self.assertContains(response, "humanresources.vemployeedepartment")

        self.assertTrue(Dataset.objects.filter(name="humanresources.employee").exists())
        self.assertTrue(Dataset.objects.filter(name="humanresources.vemployeedepartment").exists())

    def test_update_dataset(self):
        """If a dataset is updated using the view, the updated dataset should be shown in the index navbar."""
        dataset = baker.make("datasets.Dataset", name="test dataset", owner=self.user)

        form_data = {"title": "updated test dataset", "owner": self.user.id}
        self.client.post(reverse("datasets:update_dataset", kwargs={"pk": dataset.id}), form_data)

        response = self.client.get(reverse("datasets:index"))

        self.assertContains(response, "updated test dataset")
        self.assertTrue(Dataset.objects.filter(title="updated test dataset").exists())

    def test_delete_dataset(self):
        """If a dataset is deleted using the view, it should be removed from the index navbar."""
        dataset = baker.make("datasets.Dataset", name="test dataset", owner=self.user)
        self.client.get(reverse("datasets:delete_dataset", kwargs={"pk": dataset.id}))

        self.assertFalse(Dataset.objects.filter(name="test dataset").exists())

    def test_import_datasets_viable_connections(self):
        """When importing datasets, the only viable connections should be those the user has permission for."""
        unowned_connection = baker.make("datasets.Connection", name="unowned connection")
        form = ImportDatasetsModelForm(user=self.user)

        self.assertTrue(form.fields["connection"].queryset.filter(id=self.connection.id).exists())
        self.assertFalse(form.fields["connection"].queryset.filter(id=unowned_connection.id).exists())

    def test_connection_datasets(self):
        """When a connection id is given, it should return all viable datasets for the connection (tables and views)."""
        data = {"connection_id": self.connection.id}
        response = self.client.get(reverse("datasets:connection_datasets"), data)

        human_resources_tables = response.context["connection_datasets"]["Tables"]["humanresources"]
        self.assertIn({"value": "humanresources.employee", "display": "employee"}, human_resources_tables)
        self.assertIn({"value": "humanresources.jobcandidate", "display": "jobcandidate"}, human_resources_tables)

        human_resources_views = response.context["connection_datasets"]["Views"]["humanresources"]
        self.assertIn({"value": "humanresources.vemployee", "display": "vemployee"}, human_resources_views)
        self.assertIn({"value": "humanresources.vjobcandidate", "display": "vjobcandidate"}, human_resources_views)

    def test_connection_datasets_exclude_existing_datasets(self):
        """If a dataset already exists, it should be excluded from the returned viable datasets for the connection."""
        # Creating a dataset that should be excluded when returning future viable datasets.
        baker.make("datasets.Dataset", name="humanresources.employee", type="TABLE", table="humanresources.employee",
                   connection=self.connection)

        # Setting "select_multiple" to True to simulate the request coming from the import datasets modal.
        data = {"connection_id": self.connection.id, "select_multiple": "True"}
        response = self.client.get(reverse("datasets:connection_datasets"), data)

        human_resources_tables = response.context["connection_datasets"]["Tables"]["humanresources"]
        self.assertNotIn({"value": "humanresources.employee", "display": "employee"}, human_resources_tables)
