from django.test import TestCase

from users.forms import UserRegisterForm
from users.models import User


class RegisterFormTest(TestCase):
    def setUp(self):
        self.user_data = {"email": "testmail@mail.com", "first_name": "Anders", "last_name": "Andersen",
                          "phone": "+4512345678", "password1": "secretpassword1", "password2": "secretpassword1"}
        self.user = User.objects.create_user(email="test@test.com", password="test")

    def test_register_form_correct(self):
        form = UserRegisterForm(data=self.user_data)

        self.assertTrue(form.is_valid())
        
    def test_register_form_email_wrong_failure(self):
        self.user_data["email"] = "test"
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "Enter a valid email address.")
        
    def test_register_form_email_exist_failure(self):
        self.user_data["email"] = "test@test.com"
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "User with this Email address already exists.")
        
    def test_register_form_email_empty_failure(self):
        self.user_data["email"] = ""
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "This field is required.")

    def test_register_form_firstname_failure(self):
        self.user_data["first_name"] = ""
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["first_name"][0], "This field is required.")

    def test_register_form_lastname_failure(self):
        self.user_data["last_name"] = ""
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["last_name"][0], "This field is required.")

    def test_register_form_phone_wrong_string_failure(self):
        self.user_data["phone"] = "number"
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"][0],
                         "Phone number must be entered in the format: '+4512345678'. Up to 15 digits allowed.")

    def test_register_form_phone_wrong_land_code_failure(self):
        self.user_data["phone"] = "12345678"
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"][0],
                         "Phone number must be entered in the format: '+4512345678'. Up to 15 digits allowed.")

    def test_register_form_phone_empty_failure(self):
        self.user_data["phone"] = ""
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"][0], "This field is required.")

    def test_register_form_password_empty_failure(self):
        self.user_data["password1"] = ""
        form = UserRegisterForm(data=self.user_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password1"][0], "This field is required.")
