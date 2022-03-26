import shutil

from django.urls import reverse
from model_bakery import baker

from datalakes.models import LocalDatalake
from settings.models import Settings, Contact
from users.models import UserProfile
from util.test_util import ClientLoginTestCase


class SettingsTests(ClientLoginTestCase):
    def setUp(self):
        super(SettingsTests, self).setUp()

        baker.make("users.UserProfile", user=self.user, first_name="test")
        self.settings = baker.make("settings.Settings", try_live_connection=False)

        self.user.is_staff = True
        self.user.save()

    @classmethod
    def tearDownClass(cls):
        super(SettingsTests, cls).tearDownClass()

        shutil.rmtree("test_root")
        shutil.rmtree("updated_root")

    def test_update_settings(self):
        """When the form is updated, both the fields of the settings model and the user profile should be updated."""
        form_data = {"try_live_connection": True, "profile_expected_datasets_n": 10, "profile_failed_threshold": 0.5,
                     "profile_delta_deviation": 0.2, "email_host_user": "email host user", "email_host": "localhost",
                     "email_host_password": "email host password", "email_port": 587, "email_use_tls": True,
                     "timezone": "UTC", "first_name": "first", "last_name": "last", "phone": 12345678,
                     "email": self.user.email}

        self.client.post(reverse("settings:settings", kwargs={"pk": self.settings.id}), form_data)

        self.assertTrue(Settings.objects.filter(try_live_connection=True).exists())
        self.assertTrue(UserProfile.objects.filter(first_name="first").exists())

    def test_create_datalake(self):
        """When a datalake is created, the datalake object should be created and assigned to the settings."""
        form_data = {"type": "LOCAL", "root_path": "test_root"}
        self.client.post(reverse("settings:create_datalake_connection"), form_data)

        self.assertTrue(LocalDatalake.objects.filter(root_path="test_root").exists())
        self.assertIsNotNone(Settings.objects.get().datalake)

    def test_update_datalake(self):
        baker.make("datalakes.LocalDatalake", root_path="")

        form_data = {"type": "LOCAL", "root_path": "updated_root"}
        self.client.post(reverse("settings:update_datalake_connection"), form_data)

        self.assertTrue(LocalDatalake.objects.filter(root_path="updated_root").exists())

    def test_delete_datalake(self):
        datalake = baker.make("datalakes.LocalDatalake", root_path="")
        self.settings.datalake = datalake
        self.settings.save()

        self.client.post(reverse("settings:delete_datalake_connection", kwargs={"pk": datalake.id}))

        self.assertFalse(LocalDatalake.objects.filter(root_path="").exists())
        self.assertIsNone(Settings.objects.get().datalake)

    def test_add_contact(self):
        self.client.post(reverse("settings:add_contact"), {"name": "test", "email": "test@test.com"})

        self.assertTrue(Contact.objects.filter(name="test", email="test@test.com").exists())

    def test_delete_contact(self):
        contact = baker.make("settings.Contact", name="test")
        self.client.post(reverse("settings:delete_contact", kwargs={"contact_id": contact.id}))

        self.assertFalse(Contact.objects.filter(name="test").exists())
