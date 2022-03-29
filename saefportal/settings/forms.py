from bootstrap_modal_forms.forms import BSModalForm
from django import forms

from settings.models import Settings
from users.models import UserProfile


class SettingsModelForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ["timezone", "dataset_refresh_frequency", "delete_outdated_frequency", "delete_outdated_threshold",
                  "try_live_connection", "profile_expected_datasets_n", "profile_failed_threshold",
                  "profile_delta_deviation", "email_host_user", "email_host_password", "email_host", "email_port",
                  "email_use_tls"]
        widgets = {
            "timezone": forms.Select(attrs={'class': "selectpicker"}),
            "profile_expected_datasets_n": forms.NumberInput(attrs={"min": "1"}),
            "profile_failed_threshold": forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.05"}),
            "profile_delta_deviation": forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.05"}),
            "email_host_password": forms.PasswordInput(render_value=True),
            "delete_outdated_threshold": forms.NumberInput(attrs={"min": "0"})
        }
        labels = {
            "profile_expected_datasets_n": "Number of datasets for expected",
            "profile_failed_threshold": "Degree of change fail threshold",
            "profile_delta_deviation": "Expected dataset deviation scale",
            "email_host_user": "Host user",
            "email_host_password": "Host password",
            "email_host": "Host",
            "email_port": "Port",
            "email_use_tls": "Use TLS"
        }

    def get_profile_task_fields(self):
        return [self["profile_failed_threshold"], self["profile_expected_datasets_n"], self["profile_delta_deviation"]]

    def get_grouped_email_fields(self):
        return [[self["email_host_user"], self["email_host_password"]], [self["email_host"], self["email_port"]]]


class UserProfileModelForm(forms.ModelForm):
    email = forms.CharField(max_length=100)

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "phone"]

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["first_name"], self["last_name"]], [self["email"], self["phone"]]]


class DatalakeConnectionModelForm(BSModalForm):
    """Empty form used since Django Bootstrap Modal Forms requires a form."""
    pass
