from django.test import TestCase
from django.urls import reverse

from ..forms import LoginForm
from ..models import User
from utils.test_utils import load_test_json, load_test_database, load_test_dataset

from saefportal.settings import MSG_SUCCESS_USER_LOGIN, MSG_ERROR_USER_LOGIN_INCORRECT, MSG_INFO_USER_LOGIN_DEACTIVATED

test_data = load_test_json('users')    

class LoginFormTest(TestCase):
    def setUp(self):
        self.form_data = {'email': 'test@test.com', 'password': 'testtest22'}

    def test_loginform_correct(self):
        form = LoginForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_loginform_email_failure(self):
        self.form_data['email'] = 'test'
        form = LoginForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')


class LoginViewTest(TestCase):
    """
    Testcases for logging in to the system
    """
    
    @classmethod
    def setUpTestData(cls):
        load_test_dataset()
        
    def setUp(self):
        self.credentials = {'email': 'test@test.com', 'password': 'test'}
        self.user = User.objects.create_user(email='test@test.com', password='test')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')
        self.failUnless(isinstance(response.context['form'], LoginForm))

    def test_login_success(self):
        result = self.client.login(email=self.credentials['email'], password=self.credentials['password'])
        self.assertTrue(result)

    def test_login_failure(self):
        result = self.client.login(email=self.credentials['email'], password='wrong')
        self.assertFalse(result)

    def test_login_response_user(self):
        response = self.client.post('/user/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'])

    def test_login_response_message_success(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post('/user/login/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_LOGIN)

    def test_login_response_message_format(self):
        self.user.is_active = True
        self.user.save()

        self.credentials['email'] = 'TEST@test.com'

        response = self.client.post('/user/login/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_LOGIN)
        
    def test_login_response_message_approve(self):
        response = self.client.post('/user/login/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_INFO_USER_LOGIN_DEACTIVATED)

    def test_login_response_message_wrong(self):
        self.credentials['password'] = 'wrong'
        response = self.client.post('/user/login/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_ERROR_USER_LOGIN_INCORRECT)
        
