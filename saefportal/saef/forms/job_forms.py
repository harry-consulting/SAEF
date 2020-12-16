from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from saef.models import Job


class AddJobForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_job_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save", css_class="btn-success"))

    class Meta:
        model = Job
        fields = ['application', 'name', 'description']


class UpdateJobForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "update_job_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save", css_class="btn-success"))
        self.helper.add_input(Submit("Operation", "Delete", css_class="btn-danger", formnovalidate='formnovalidate'))

    class Meta:
        model = Job
        fields = ['application', 'name', 'description']
