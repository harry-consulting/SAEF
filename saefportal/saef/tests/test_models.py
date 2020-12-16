from django.test import TestCase
from ..models import ApplicationToken, Application

def create_application_token():
    new_token = ApplicationToken(
        name="test_token",
        business_owner=" test owner",
        application_group_name="test group",
        created_by="test user"
    )
    new_token.save()
    return new_token


class TestModels(TestCase):
    def test_application_token(self):
        """
            validate the analyze_dataset function
        """
        new_token = create_application_token()
        token_value = new_token.application_token
        token = ApplicationToken.objects.get(pk=new_token.pk)
        result = token.application_token
        self.assertEqual(token_value, result)

    def test_application_key(self):
        application_token = create_application_token()
        new_application = Application(
            name="test_application",
            description="test description",
            application_token=application_token
        )

        new_application.save()
        key_value = new_application.application_key
        token = Application.objects.get(pk=new_application.pk)
        result = token.application_key
        self.assertEqual(key_value, result)
