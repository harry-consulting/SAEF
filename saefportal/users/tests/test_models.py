from django.test import TestCase

from ..models import User

class UserManagersTest(TestCase):
    """
    Testcases for custom user model
    """
    def test_create_user(self):
        user = User.objects.create_user(email='test@test.com', password='test')
        self.assertEqual(user.email, 'test@test.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
     
    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(email='testsuper@test.com', password='test')
        self.assertEqual(admin_user.email, 'testsuper@test.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)