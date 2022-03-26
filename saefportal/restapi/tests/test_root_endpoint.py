from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User


class RootTests(APITestCase):
    def setUp(self):
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email=self.credentials['email'], password=self.credentials['password'])
        self.client.force_authenticate(user=self.user)

    def test_root(self):
        """Ensure that the root endpoint links to all necessary endpoints."""
        response = self.client.get(reverse("api-root"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "connections")
        self.assertContains(response, "datasets")
        self.assertContains(response, "dataset runs")
        self.assertContains(response, "jobs")
        self.assertContains(response, "job runs")
        self.assertContains(response, "users")
        self.assertContains(response, "contacts")
        self.assertContains(response, "settings")
        self.assertContains(response, "profile dataset")
        self.assertContains(response, "refresh data")
        self.assertContains(response, "extract metadata")
        self.assertContains(response, "read data")
