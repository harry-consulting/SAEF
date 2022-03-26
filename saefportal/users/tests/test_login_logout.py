from django.test import TestCase
from django.urls import reverse

from users.forms import LoginAuthForm
from users.models import User


class LoginFormTests(TestCase):
    def setUp(self):
        self.credentials = {"username": "test@test.com", "password": "test"}
        self.user = User.objects.create_user(email=self.credentials["username"], password=self.credentials["password"])

    def test_login_form_correct(self):
        self.user.is_active = True
        self.user.save()

        form = LoginAuthForm(data=self.credentials)

        self.assertTrue(form.is_valid())

    def test_login_form_account_not_approved_failure(self):
        form = LoginAuthForm(data=self.credentials)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "Your account has not been approved yet.")

    def test_login_form_email_failure(self):
        self.credentials["username"] = "test"
        form = LoginAuthForm(data=self.credentials)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "You have entered your email or password incorrectly.")


class LoginViewTests(TestCase):
    def setUp(self):
        self.credentials = {"email": "test@test.com", "password": "test"}
        self.user = User.objects.create_user(email="test@test.com", password="test")

    def test_login_view_get(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/authentication/login.html")

    def test_login_success(self):
        result = self.client.login(email=self.credentials["email"], password=self.credentials["password"])
        self.assertTrue(result)

    def test_login_failure(self):
        result = self.client.login(email=self.credentials["email"], password="wrong")
        self.assertFalse(result)


class LogoutViewTests(TestCase):
    def test_logout(self):
        self.credentials = {"email": "test@test.com", "password": "test"}
        self.user = User.objects.create_user(email=self.credentials["email"], password=self.credentials["password"])
        self.client.login(email=self.credentials["email"], password=self.credentials["password"])

        response = self.client.get(reverse("logout"), follow=True)

        self.assertRedirects(response, reverse("login"))
