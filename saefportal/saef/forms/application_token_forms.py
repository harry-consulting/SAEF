from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from saef.models import ApplicationToken


class AddApplicationTokenForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_application_token_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Save", css_class="btn-success"))
        self.fields["name"].initial = ""

    class Meta:
        model = ApplicationToken
        fields = ["name", "business_owner", "application_group_name", "created_by"]


class UpdateApplicationTokenForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "update_application_token_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save", css_class="btn-success"))
        self.helper.add_input(Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate"))

    class Meta:
        model = ApplicationToken
        fields = ["name", "business_owner", "application_group_name", "created_by"]
