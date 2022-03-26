from django.test import TestCase
from django.urls import reverse
from users.models import User


class LoginRedirectsTests(TestCase):
    def test_redirect_saef_not_logged_in(self):
        def test_redirect_saef_not_logged_in(path, status_code=302):
            response = self.client.get(path, follow=True)
            self.assertRedirects(response, f"/user/login/?next={path}", status_code=status_code)

        test_redirect_saef_not_logged_in(reverse("home"))
        test_redirect_saef_not_logged_in(reverse("datasets:index"))
        test_redirect_saef_not_logged_in(reverse("jobs:index"))


class TopNavigationTests(TestCase):
    def test_navigation_href_logged_out(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'href="/user/register/"')
        self.assertContains(response, 'href="/user/login/"')

    def test_navigation_href(self):
        User.objects.create_user(email="test@test.com", password="test")
        self.client.login(email="test@test.com", password="test")

        response = self.client.get(reverse("login"))

        self.assertContains(response, 'href="/"')
        self.assertContains(response, 'href="/manage')
        self.assertContains(response, 'href="/jobs')
        self.assertContains(response, 'href="/user/logout')
        self.assertContains(response, 'href="/settings')
