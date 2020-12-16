
import copy

from django.urls import reverse
from django.test import TestCase

from ..models import User
from ..forms import UserRegisterForm
from utils.test_utils import load_test_json, load_test_database

from saefportal.settings import MSG_SUCCESS_USER_REGISTER

test_data = load_test_json('users')    

class RegisterFormTest(TestCase):
    """
    Testcases for RegisterForm
    """        
    def setUp(self):
        self.data = copy.deepcopy(test_data)    
        self.user = User.objects.create_user(email='test@test.com', password='test')
        
    def test_registerform_correct(self):
        form = UserRegisterForm(data=self.data['user'])
        self.assertTrue(form.is_valid())
        
    def test_registerform_email_wrong_failure(self):
        self.data['user']['email'] = 'test'
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')
        
    def test_registerform_email_exist_failure(self):
        self.data['user']['email'] = 'test@test.com'
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'User with this Email address already exists.')
        
    def test_registerform_email_empty_failure(self):
        self.data['user']['email'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'This field is required.')
        
    def test_registerform_firstname_failure(self):
        self.data['user']['firstname'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['firstname'][0], 'This field is required.')
        
    def test_registerform_lastname_failure(self):
        self.data['user']['lastname'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['lastname'][0], 'This field is required.')
        
    def test_registerform_organization_failure(self):
        self.data['user']['organization'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['organization'][0], 'This field is required.')
        
    def test_registerform_phone_wrong_string_failure(self):
        self.data['user']['phone'] = 'number'
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['phone'][0], "Phone number must be entered in the format: '+4512345678'. Up to 15 digits allowed.")
        
    def test_registerform_phone_wrong_landcode_failure(self):
        self.data['user']['phone'] = '12345678'
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['phone'][0], "Phone number must be entered in the format: '+4512345678'. Up to 15 digits allowed.")
        
    def test_registerform_phone_empty_failure(self):
        self.data['user']['phone'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['phone'][0], 'This field is required.')
        
    def test_registerform_password_empty_failure(self):
        self.data['user']['password1'] = ''
        form = UserRegisterForm(data=self.data['user'])
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'][0], 'This field is required.')
        
        
class RegisterViewTest(TestCase):
    """
    Testcases for registering in to the system
    """
    def setUp(self):
        self.data = copy.deepcopy(test_data)
        
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/register.html')
        self.failUnless(isinstance(response.context['form'], UserRegisterForm))

    def test_register_account(self):
        response = self.client.post('/user/register/', self.data['user'], follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_REGISTER(self.data['user']['email']))
        
    def test_register_redirect_login(self):
        response = self.client.post('/user/register/', self.data['user'], follow=True)
        self.assertRedirects(response, '/user/login/')