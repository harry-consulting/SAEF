from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import (Textarea, TextInput, Select, SelectMultiple, ModelChoiceField, CharField, FileField,
                          ClearableFileInput)

from datasets.models import Connection, Dataset
from users.mixins import LogOwnerUpdatesMixin
from users.models import User


class CreateConnectionModelForm(BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))

    class Meta:
        model = Connection
        fields = ["name", "owner", "type"]
        widgets = {"name": TextInput(attrs={"placeholder": "Name"})}

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["name"], self["owner"]]]


class UpdateConnectionModelForm(LogOwnerUpdatesMixin, BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))

    class Meta:
        model = Connection
        fields = ["title", "owner"]

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["title"], self["owner"]]]


class QueryDatasetModelForm(BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))
    file_id = CharField(required=False, widget=TextInput(attrs={"class": "d-none"}))
    query = CharField(required=True, widget=Textarea(attrs={"class": "form-control", "rows": "2",
                                                            "placeholder": "SQL query"}))

    def __init__(self, user, *args, **kwargs):
        super(QueryDatasetModelForm, self).__init__(*args, **kwargs)

        # Only show the connections that the user has permission for.
        user_connections = [connection.id for connection in Connection.objects.all()
                            if user.has_permission("update_connection", connection)]
        self.fields["connection"] = ModelChoiceField(queryset=Connection.objects.filter(id__in=user_connections))

    class Meta:
        model = Dataset
        fields = ["name", "description", "tags", "contacts", "owner", "connection", "query", "file_id"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Name"}),
            "description": Textarea(attrs={"placeholder": "Description"}),
            "tags": TextInput(attrs={"placeholder": "Comma-separated"}),
            "contacts": SelectMultiple(attrs={"class": "selectpicker", "multiple": "on"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["name"], self["owner"]], [self["description"]], [self["tags"], self["contacts"]]]


class ImportDatasetsModelForm(BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))

    def __init__(self, user, *args, **kwargs):
        super(ImportDatasetsModelForm, self).__init__(*args, **kwargs)

        # Only show the connections that the user has permission for.
        user_connections = [connection.id for connection in Connection.objects.all()
                            if user.has_permission("update_connection", connection)]
        self.fields["connection"] = ModelChoiceField(queryset=Connection.objects.filter(id__in=user_connections))

    class Meta:
        model = Dataset
        fields = ["tags", "contacts", "owner", "connection"]
        widgets = {
            "tags": TextInput(attrs={"placeholder": "Comma-separated"}),
            "contacts": SelectMultiple(attrs={"class": "selectpicker", "multiple": "on"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["tags"], self["contacts"]], [self["owner"]]]


class UploadDatasetsModelForm(BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))
    files = FileField(widget=ClearableFileInput(attrs={"multiple": True}))

    class Meta:
        model = Dataset
        fields = ["tags", "contacts", "owner"]
        widgets = {
            "tags": TextInput(attrs={"placeholder": "Comma-separated"}),
            "contacts": SelectMultiple(attrs={"class": "selectpicker", "multiple": "on"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["tags"], self["contacts"]], [self["owner"]]]


class UpdateDatasetModelForm(LogOwnerUpdatesMixin, BSModalModelForm):
    owner = ModelChoiceField(queryset=User.objects.all(), required=True, widget=Select(attrs={"class": "form-select"}))

    class Meta:
        model = Dataset
        fields = ["title", "description", "tags", "contacts", "owner"]
        widgets = {
            "description": Textarea(attrs={"placeholder": "Description"}),
            "tags": TextInput(attrs={"placeholder": "Comma-separated"}),
            "contacts": SelectMultiple(attrs={"class": "selectpicker", "multiple": "on"}),
        }

    def get_grouped_fields(self):
        """Grouping fields for easier handling in the template."""
        return [[self["title"], self["owner"]], [self["description"]], [self["tags"], self["contacts"]]]
