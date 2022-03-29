from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.forms import TextInput, Textarea, Select, DateTimeInput, ModelChoiceField

from jobs.models import Job
from users.mixins import LogOwnerUpdatesMixin
from users.models import User


class JobModelForm(LogOwnerUpdatesMixin, BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))
    schedule_start_time = forms.DateTimeField(label="Start datetime", required=True,
                                              widget=DateTimeInput(attrs={"class": "datepicker"}))

    class Meta:
        model = Job
        fields = ["name", "owner", "description", "template_task", "alert_on_start_email", "alert_on_success_email",
                  "alert_on_failure_email", "schedule_start_time"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Name"}),
            "description": Textarea(attrs={"placeholder": "Description"}),
            "template_task": Select(attrs={"class": "form-select"}),
            "alert_on_start_email": TextInput(attrs={"placeholder": "Emails (comma-separated)"}),
            "alert_on_success_email": TextInput(attrs={"placeholder": "Emails (comma-separated)"}),
            "alert_on_failure_email": TextInput(attrs={"placeholder": "Emails (comma-separated)"}),
        }

    def get_alert_group(self):
        """Grouping fields for easier handling in the template."""
        return [self["alert_on_start_email"], self["alert_on_success_email"], self["alert_on_failure_email"]]
