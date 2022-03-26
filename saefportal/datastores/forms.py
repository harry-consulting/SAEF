from django.forms import ModelForm, TextInput, PasswordInput, Form, CharField

from datastores.models import AzureDatastore, PostgresDatastore


class PostgresDatastoreModelForm(ModelForm):
    class Meta:
        model = PostgresDatastore
        fields = ["database_name", "username", "password", "host", "port"]
        widgets = {
            "database_name": TextInput(attrs={"placeholder": "Database name"}),
            "username": TextInput(attrs={"placeholder": "Name"}),
            "password": PasswordInput(attrs={"placeholder": "Password"}),
            "host": TextInput(attrs={"placeholder": "Host"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["database_name"]], [self["username"], self["password"]], [self["host"], self["port"]]]


class AzureDatastoreModelForm(ModelForm):
    class Meta:
        model = AzureDatastore
        fields = ["database_name", "username", "password", "host", "port"]
        widgets = {
            "database_name": TextInput(attrs={"placeholder": "Database name"}),
            "username": TextInput(attrs={"placeholder": "Name"}),
            "password": PasswordInput(attrs={"placeholder": "Password"}),
            "host": TextInput(attrs={"placeholder": "Host"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["database_name"]], [self["username"], self["password"]], [self["host"], self["port"]]]


class FileDatastoreForm(Form):
    """Form used for OneDrive, Google Drive and Dropbox connections."""
    root_path = CharField(required=False, max_length=500,
                          widget=TextInput(attrs={"placeholder": "Path to home of SAEF datalake"}))

    def get_grouped_fields(self):
        return [[self["root_path"]]]


class GoogleCloudStorageDatastoreForm(Form):
    project_id = CharField(label="Project ID", max_length=100, required=True,
                           widget=TextInput(attrs={"placeholder": "GCP project ID"}))
    bucket_name = CharField(max_length=500, required=True,
                            widget=TextInput(attrs={"placeholder": "GCP bucket name"}))

    def get_grouped_fields(self):
        return [[self["project_id"], self["bucket_name"]]]


class AzureDatastoreForm(Form):
    connection_string = CharField(max_length=200, required=True,
                                  widget=TextInput(attrs={"placeholder": "Connection string"}))
    blob_container = CharField(max_length=200, required=True,
                               widget=TextInput(attrs={"placeholder": "Blob container"}))

    def get_grouped_fields(self):
        return [[self["connection_string"], self["blob_container"]]]


class AmazonS3DatastoreForm(Form):
    access_key_id = CharField(max_length=200, required=True,
                              widget=TextInput(attrs={"placeholder": "AWS access key ID"}))
    secret_access_key = CharField(max_length=200, required=True,
                                  widget=TextInput(attrs={"placeholder": "AWS secret access key"}))
    bucket_name = CharField(max_length=200, required=True,
                            widget=TextInput(attrs={"placeholder": "Amazon S3 bucket name"}))

    def get_grouped_fields(self):
        return [[self["access_key_id"], self["secret_access_key"], self["bucket_name"]]]
