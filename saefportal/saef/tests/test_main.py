from django.test import TestCase
from django.urls import reverse
from users.models import User


class LoginRedirectsTest(TestCase):
    def test_redirect_saef_not_logged_in(self):
        def test_redirect_saef_not_logged_in(path, status_code=302):
            response = self.client.get(path, follow=True)
            self.assertRedirects(response, f'/user/login/?next={path}', status_code=status_code)

        test_redirect_saef_not_logged_in('/saef/')
        test_redirect_saef_not_logged_in('/saef/manage/')
        test_redirect_saef_not_logged_in('/saef/application/2/')
        test_redirect_saef_not_logged_in('/saef/application/add/')
        test_redirect_saef_not_logged_in('/saef/application_token')
        test_redirect_saef_not_logged_in('/saef/application_token/5/')
        test_redirect_saef_not_logged_in('/saef/application_token/add/')
        test_redirect_saef_not_logged_in('/saef/job/')
        test_redirect_saef_not_logged_in('/saef/job/5/')
        test_redirect_saef_not_logged_in('/saef/job/add/')
        test_redirect_saef_not_logged_in('/saef/connection/')
        test_redirect_saef_not_logged_in('/saef/connection/5/')
        test_redirect_saef_not_logged_in('/saef/connection/add/')
        test_redirect_saef_not_logged_in('/saef/dataset/')
        test_redirect_saef_not_logged_in('/saef/dataset/5/')
        test_redirect_saef_not_logged_in('/saef/dataset/add/')
        test_redirect_saef_not_logged_in('/saef/column/manage/5/')
        test_redirect_saef_not_logged_in('/saef/constraint/manage/5/')
        test_redirect_saef_not_logged_in('/saef/5/')
        test_redirect_saef_not_logged_in('/saef/application_session')
        
class TopNavigationTest(TestCase):
    def test_navigation_href_logged_out(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'href="/saef/"')
        self.assertContains(response, 'href="/saef/manage"')
        self.assertContains(response, 'href="/analyzer"')
        self.assertContains(response, 'href="/control"')

        self.assertContains(response, 'href="/user/register"')
        self.assertContains(response, 'href="/user/login"')

    def test_navigation_href_normal_user(self):
        User.objects.create_user(email='test@test.com', password='test')
        self.client.login(email='test@test.com', password='test')

        response = self.client.get(reverse('login'))
        self.assertContains(response, 'href="/saef/"')
        self.assertContains(response, 'href="/saef/manage"')
        self.assertContains(response, 'href="/analyzer"')
        self.assertContains(response, 'href="/control"')

        self.assertContains(response, 'href="/settings"')
        self.assertContains(response, 'href="/user/logout"')

    def test_navigation_href_super_user(self):
        User.objects.create_superuser(email='test@test.com', password='test')
        self.client.login(email='test@test.com', password='test')

        response = self.client.get(reverse('login'))
        self.assertContains(response, 'href="/saef/"')
        self.assertContains(response, 'href="/saef/manage"')
        self.assertContains(response, 'href="/analyzer"')
        self.assertContains(response, 'href="/control"')

        self.assertContains(response, 'href="/user/admin"')
        self.assertContains(response, 'href="/settings"')
        self.assertContains(response, 'href="/user/logout"')