from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.forms import ModelForm
from saef.models import Dataset


class SelectConnectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "select_connection_form"
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("connection", onchange="form.submit();")
        )

    class Meta:
        model = Dataset
        fields = ["connection"]


class AddDatasetForm(ModelForm):
    def __init__(self, dataset_table_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "id_add_dataset_form"
        self.helper.form_name = "add_dataset_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection", onchange="form.submit();"),
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            Field("dataset_access_method", onChange="selectRelevant();"),
            "dataset_extraction_table",
            "dataset_extraction_sql",
            Submit("Operation", "Save", css_class="btn-success", onClick="removeRequired();")
        )
        self.fields["dataset_extraction_table"].choices = dataset_table_choices

    dataset_extraction_table = forms.ChoiceField(choices=(), required=False)
    dataset_extraction_sql = forms.CharField(label="SQL query (LIMIT 50)", widget=forms.Textarea)

    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_access_method",
            "dataset_extraction_table",
            "dataset_extraction_sql"
        ]


class DatasetWithoutSQLForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_access_method",
            "dataset_extraction_table"
        ]


class DatasetWithoutTableForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_access_method",
            "dataset_extraction_sql"
        ]


class EditDatasetForm(ModelForm):
    def __init__(self, dataset_table_choices, enabled_manage=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "edit_dataset_form"
        self.helper.form_method = "post"
        self.fields["dataset_extraction_table"].choices = dataset_table_choices
        main_layout = Layout(
            Field("connection", onChange="form.submit();", formnovalidate="formnovalidate"),
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            Field("dataset_access_method", onChange="selectRelevant();"),
            Field("dataset_extraction_table"),
            Field("dataset_extraction_sql"),
            Submit("Operation", "Save", css_class="btn-success", onClick="removeRequired();"),
            Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate"),
        )
        if enabled_manage:
            manage_layout = Layout(
                Submit("Operation", "Manage Column", css_class="btn-info", formnovalidate="formnovalidate"),
                Submit("Operation", "Manage Constraint", css_class="btn-info", formnovalidate="formnovalidate"),
            )
        else:
            manage_layout = Layout()

        self.helper.layout = Layout(
            main_layout,
            manage_layout,
            Submit("Operation", "Preview", css_class="btn-info", onClick="removeRequired();")
        )

    dataset_extraction_table = forms.ChoiceField(choices=(), required=False)
    dataset_extraction_sql = forms.CharField(label="SQL query (LIMIT 50)", widget=forms.Textarea)

    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_access_method",
            "dataset_extraction_table",
            "dataset_extraction_sql"
        ]


class AddAzureBlobStorageDatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "id_add_azure_blob_storage_dataset_form"
        self.helper.form_name = "add_azure_blob_storage_dataset_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection", onchange="form.submit();"),
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_extraction_sql",
            Submit("Operation", "Save", css_class="btn-success", onClick="return verifyDatasetName();")
        )

    dataset_extraction_sql = forms.CharField(label="SQL query (LIMIT 50)", widget=forms.Textarea)

    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_extraction_sql"
        ]


class EditAzureBlobStorageDatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "edit_azure_blob_storage_dataset_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("connection", onChange="form.submit();", formnovalidate="formnovalidate"),
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            Field("dataset_extraction_sql"),
            Submit("Operation", "Save", css_class="btn-success",
                   onClick="removeRequired(); return verifyDatasetName();"),
            Submit("Operation", "Delete", css_class="btn-danger", formnovalidate="formnovalidate"),
            Submit("Operation", "Manage Column", css_class="btn-info", formnovalidate="formnovalidate"),
            Submit("Operation", "Preview", css_class="btn-info")
        )

    dataset_extraction_sql = forms.CharField(label="SQL query (LIMIT 50)", widget=forms.Textarea)

    class Meta:
        model = Dataset
        fields = [
            "connection",
            "job",
            "sequence_in_job",
            "dataset_name",
            "dataset_type",
            "query_timeout",
            "dataset_extraction_sql"
        ]
