from django.urls import reverse
from model_bakery import baker

from util.test_util import ClientLoginDatalakeTestCase


class SearchTests(ClientLoginDatalakeTestCase):
    @classmethod
    def setUpTestData(cls):
        super(SearchTests, cls).setUpTestData()

        cls.dataset_1 = baker.make("datasets.Dataset", name="employee", tags="tag")
        cls.dataset_2 = baker.make("datasets.Dataset", name="person", tags="tag")

    def test_search_name(self):
        """If a search is made, datasets whose name matches the search should be shown."""
        response = self.client.get(reverse("datasets:search_datasets"), {"q": "employee"})

        self.assertContains(response, "employee")
        self.assertQuerysetEqual(response.context["search_datasets"], [self.dataset_1], transform=lambda x: x)

    def test_search_tags(self):
        """If a search is made, datasets whose tags match the search should be shown."""
        response = self.client.get(reverse("datasets:search_datasets"), {"q": "tag"})

        self.assertContains(response, "employee")
        self.assertContains(response, "person")
        self.assertQuerysetEqual(response.context["search_datasets"], [self.dataset_1, self.dataset_2],
                                 transform=lambda x: x, ordered=False)
