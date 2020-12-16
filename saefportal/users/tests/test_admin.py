
import json
import os
import copy

from django.urls import reverse
from django.test import TestCase

from pathlib import Path
from ..models import User
from utils.test_utils import load_test_json, load_test_database

from saefportal.settings import MSG_SUCCESS_USER_ACTIVATED, MSG_SUCCESS_USER_DEACTIVATED

test_data = load_test_json('users')
    
class AdminViewTest(TestCase):
    """
    Testcases for admin system
    """
    def setUp(self):
        self.data = copy.deepcopy(test_data)
    
    def test_admin_view_get_no_access(self):
        response = self.client.get(reverse('admin'))
        self.assertRedirects(response, '/admin/login/?next=/user/admin/')
        
    def test_admin_view_get_success(self):
        # Creates an user to be rendered on the admin page
        self.client.post('/user/register/', self.data['user'], follow=True)
        
        User.objects.create_superuser(email='test@test.com', password='test')
        self.client.login(email='test@test.com', password='test')
        
        response = self.client.get(reverse('admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/admin.html')
        self.assertContains(response, 'John Carlson')
        
        
class AdminUserHandleTest(TestCase):
    """
    Testcases for admin system
    """
    def setUp(self):
        User.objects.create_superuser(email='superuser@test.com', password='test')
        self.user = User.objects.create_user(email='test@test.com', password='test')
       
    def test_activate_user_no_access(self):
        response = self.client.get(f'/user/activate/{self.user.pk}', follow=True)
        self.assertRedirects(response, f'/admin/login/?next=/user/activate/{self.user.pk}')
        
    def test_deactivate_user_no_access(self):
        response = self.client.get(f'/user/deactivate/{self.user.pk}', follow=True)
        self.assertRedirects(response, f'/admin/login/?next=/user/deactivate/{self.user.pk}')
        
    def test_activate_user(self):
        # Login with superuser
        self.client.login(email='superuser@test.com', password='test')
        
        # Assert that the user have been activated
        self.assertEqual(User.objects.get(pk=self.user.pk).is_active, False)
        response = self.client.get(f'/user/activate/{self.user.pk}', follow=True)
        self.assertEqual(User.objects.get(pk=self.user.pk).is_active, True)
        
        # Assert that the correct alert is given
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_ACTIVATED(self.user))
        
        # Assert that page is redirected back to admin
        self.assertRedirects(response, '/user/admin/')
        
    def test_deactivate_user(self):
        # Initial user is active
        self.user.is_active = True
        self.user.save()
        
        # Login with super user
        self.client.login(email='superuser@test.com', password='test')
        
        # Assert that the user have been deactivated
        self.assertEqual(User.objects.get(pk=self.user.pk).is_active, True)
        response = self.client.get(f'/user/deactivate/{self.user.pk}', follow=True)
        self.assertEqual(User.objects.get(pk=self.user.pk).is_active, False)
        
        # Assert that the correct alert is given
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_DEACTIVATED(self.user))
        
        # Assert that page is redirected back to admin
        self.assertRedirects(response, '/user/admin/')