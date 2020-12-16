from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from saef.models import Application


class AddApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_application_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save", css_class="btn-success"))

    class Meta:
        model = Application
        fields = ['application_token', 'name', 'description']


class UpdateApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "update_application_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save", css_class="btn-success"))
        self.helper.add_input(Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate"))

    class Meta:
        model = Application
        fields = ['application_token', 'name', 'description']
