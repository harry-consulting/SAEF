from django.test import TestCase

from ..models import User

from saefportal.settings import MSG_SUCCESS_USER_LOGOUT

class LogoutViewTest(TestCase):
    """
    Testcases for logging out of system
    """
    def test_logout(self):
        User.objects.create_user(email='test@test.com', password='test')
        self.client.login(email='test@test.com', password='test')
        
        response = self.client.get('/user/logout/', follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), MSG_SUCCESS_USER_LOGOUT)
        self.assertRedirects(response, '/user/login/')
          