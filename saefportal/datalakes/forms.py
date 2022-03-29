from django import forms


class FileStoreDatalakeForm(forms.Form):
    """Form used for OneDrive, Google Drive and Dropbox datalakes."""
    root_path = forms.CharField(max_length=500, required=False,
                                widget=forms.TextInput(attrs={"placeholder": "Path to home of SAEF datalake"}))


class GoogleCloudStorageDatalakeForm(forms.Form):
    project_id = forms.CharField(label="Project ID", max_length=100, required=True,
                                 widget=forms.TextInput(attrs={"placeholder": "GCP project ID"}))
    bucket_name = forms.CharField(max_length=500, required=False,
                                  widget=forms.TextInput(attrs={"placeholder": "GCP bucket name"}))


class AzureDatalakeForm(forms.Form):
    connection_string = forms.CharField(max_length=200, required=True,
                                        widget=forms.TextInput(attrs={"placeholder": "Storage account connection string"}))
    blob_container = forms.CharField(max_length=200, required=False,
                                     widget=forms.TextInput(attrs={"placeholder": "Storage account blob container"}))


class AmazonS3DatalakeForm(forms.Form):
    access_key_id = forms.CharField(max_length=200, required=True,
                                    widget=forms.TextInput(attrs={"placeholder": "AWS access key ID"}))
    secret_access_key = forms.CharField(max_length=200, required=True,
                                        widget=forms.TextInput(attrs={"placeholder": "AWS secret access key"}))
    bucket_name = forms.CharField(max_length=200, required=False,
                                  widget=forms.TextInput(attrs={"placeholder": "Amazon S3 bucket name"}))
