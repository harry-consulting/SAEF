from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from users.models import User, PermissionRequest, OrganizationGroup


class LoginAuthForm(AuthenticationForm):
    error_messages = {"invalid_login": "You have entered your email or password incorrectly.",
                      "inactive": "Your account has not been approved yet."}


class UserRegisterForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", max_length=32)
    last_name = forms.CharField(label="Last Name", max_length=32)
    phone_regex = RegexValidator(regex=r"^\+?1?\d{9,15}$", message="Phone number must be entered in the format: "
                                                                   "'+4512345678'. Up to 15 digits allowed.")
    phone = forms.CharField(label="Phone Number", max_length=20, validators=[phone_regex])
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(), validators=[validate_password])
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password1", "password2"]

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()

        if "password1" in cleaned_data and "password2" in cleaned_data:
            if cleaned_data["password1"] != cleaned_data["password2"]:
                raise forms.ValidationError("Passwords don't match. Please try again.")

        if "email" in cleaned_data:
            cleaned_data["email"] = cleaned_data["email"].lower()

        if "first_name" in cleaned_data and "last_name" in cleaned_data:
            cleaned_data["first_name"] = cleaned_data["first_name"].capitalize()
            cleaned_data["last_name"] = cleaned_data["last_name"].capitalize()

        return cleaned_data

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)

        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["first_name"], self["last_name"]], [self["email"]], [self["phone"]],
                [self["password1"], self["password2"]]]


class PermissionRequestModelForm(BSModalModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PermissionRequestModelForm, self).__init__(*args, **kwargs)
        self.fields["group"] = forms.ModelChoiceField(queryset=user.organization_groups.all(), required=False)

    class Meta:
        model = PermissionRequest
        fields = ["group", "message"]


class UserGroupsPermissionsModelForm(BSModalModelForm):
    organization_groups = forms.ModelMultipleChoiceField(queryset=OrganizationGroup.objects.all().exclude(name="All"),
                                                         required=False)

    class Meta:
        model = User
        fields = ["organization_groups"]
