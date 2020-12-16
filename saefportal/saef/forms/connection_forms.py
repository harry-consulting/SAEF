from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.forms import ModelForm, PasswordInput

from saef.models import Connection, PostgresConnection, AzureConnection, AzureBlobStorageConnection


class ConnectionTypeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "connection_type_form"
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("connection_type", onchange="form.submit();")
        )

    class Meta:
        model = Connection
        fields = ["connection_type"]


class AddConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_connection_form"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Operation", "Save"))
        self.helper.form_tag = False

    class Meta:
        model = Connection
        fields = ["name", "connection_type", "time_out"]


class AddPostgresConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_postgres_connection_form"
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "connection_name",
            "db_name",
            "username",
            "password",
            "host",
            "port",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
            Submit("Operation", "Test", css_class="btn-dark")
        )
        self.fields["time_out"].initial = 120

    connection_name = forms.CharField(label="Connection Name", max_length=128)
    password = forms.CharField(
        label='Password', max_length=128, widget=PasswordInput(render_value=True))
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = PostgresConnection
        fields = ["db_name", "username", "password", "host", "port"]
        labels = {"db_name": "Database Name"}


class EditPostgresConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "edit_postgres_connection_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection_type", disabled="disabled"),
            "connection_name",
            "db_name",
            "username",
            "host",
            "port",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
            Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate")
        )

    connection_type = forms.CharField(label="Connection Type")
    connection_name = forms.CharField(label="Connection Name", max_length=128)
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = PostgresConnection
        fields = ["db_name", "username", "host", "port"]
        labels = {"db_name": "Database Name"}


class AddAzureConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_azure_connection_form"
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "connection_name",
            "db_name",
            "username",
            "password",
            "host",
            "port",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
            Submit("Operation", "Test", css_class="btn-dark")
        )
        self.fields["time_out"].initial = 120

    connection_name = forms.CharField(label="Connection Name", max_length=128)
    password = forms.CharField(
        label='Password', max_length=128, widget=PasswordInput(render_value=True))
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = AzureConnection
        fields = ["db_name", "username", "password", "host", "port"]
        labels = {"db_name": "Database Name"}


class EditAzureConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "edit_azure_connection_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection_type", disabled="disabled"),
            "connection_name",
            "db_name",
            "username",
            "host",
            "port",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
            Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate")
        )

    connection_type = forms.CharField(label="Connection Type")
    connection_name = forms.CharField(label="Connection Name", max_length=128)
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = AzureConnection
        fields = ["db_name", "username", "host", "port"]
        labels = {"db_name": "Database Name"}


class AddAzureBlobStorageConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "add_azure_blob_storage_connection_form"
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "connection_name",
            "connection_string",
            "container_name",
            "blob_name",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
        )
        self.fields["time_out"].initial = 120

    connection_name = forms.CharField(label="Connection Name", max_length=128)
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = AzureBlobStorageConnection
        fields = ["connection_string", "container_name", "blob_name"]
        labels = {"connection_type": "Connection Type",
                  "connection_string": "Connection String",
                  "container_name": "Container Name",
                  "blob_name": "Blob Name"}


class EditAzureBlobStorageConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "edit_azure_blob_storage_connection_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection_type", disabled="disabled"),
            "connection_name",
            "connection_string",
            "container_name",
            "blob_name",
            "time_out",
            Submit("Operation", "Save", css_class="btn-success"),
            Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate")
        )

    connection_type = forms.CharField(label="Connection Type")
    connection_name = forms.CharField(label="Connection Name", max_length=128)
    time_out = forms.IntegerField(label="Time Out")

    class Meta:
        model = AzureBlobStorageConnection
        fields = ["connection_string", "container_name", "blob_name"]
        labels = {"connection_type": "Connection Type",
                  "connection_string": "Connection String",
                  "container_name": "Container Name",
                  "blob_name": "Blob Name"}
